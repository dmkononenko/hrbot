import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import async_session
from app.models import Employee, Survey, Question, SurveyResponse, Answer, QuestionOption
from app.bot.fsm import SurveyStates
from app.bot.keyboards.keyboards import (
    build_single_choice_keyboard,
    build_multiple_choice_keyboard,
    build_cancel_keyboard,
    build_help_keyboard
)
from app.bot.bot import bot
from app.bot.services.notification_service import NotificationService
from app.config import settings

logger = logging.getLogger(__name__)
router = Router()


async def get_db_session() -> AsyncSession:
    """Get database session."""
    async with async_session() as session:
        yield session


@router.callback_query(F.data.startswith("start_survey_"))
async def start_survey(callback: CallbackQuery, state: FSMContext):
    """Start survey when user clicks button."""
    survey_id = int(callback.data.split("_")[2])
    telegram_id = callback.from_user.id
    logger.info(f"start_survey called: survey_id={survey_id}, telegram_id={telegram_id}")

    async with async_session() as db:
        # Get employee
        emp_result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = emp_result.scalar_one_or_none()

        if not employee:
            logger.warning(f"Employee not found for telegram_id: {telegram_id}")
            await callback.message.edit_text("Сотрудник не найден. Пожалуйста, свяжитесь с HR.")
            return

        # Get pending response
        result = await db.execute(
            select(SurveyResponse).where(
                SurveyResponse.survey_id == survey_id,
                SurveyResponse.employee_id == employee.id,
                SurveyResponse.status.in_(["pending", "in_progress"])
            )
        )
        response = result.scalar_one_or_none()

        if not response:
            logger.warning(f"No pending survey found for employee_id: {employee.id}, survey_id: {survey_id}")
            await callback.message.edit_text("Нет доступных опросов.")
            return

        # Update status to in_progress
        response.status = "in_progress"
        await db.commit()

        # Get survey with questions
        survey_result = await db.execute(
            select(Survey)
            .where(Survey.id == survey_id)
            .options(selectinload(Survey.questions).selectinload(Question.options))
        )
        survey = survey_result.scalar_one_or_none()

        if not survey or not survey.questions:
            logger.error(f"Survey has no questions for survey_id: {survey_id}")
            await callback.message.edit_text("У этого опроса нет вопросов.")
            return

        # Store survey and response data in FSM
        await state.update_data(
            survey_id=survey_id,
            response_id=response.id,
            current_question_index=0,
            selected_answers=[]
        )

        # Show first question
        first_question = survey.questions[0]
        await show_question(callback.message, first_question, callback.message.bot, callback.from_user.id, state)

        await callback.answer()


async def show_question(message: Message, question: Question, bot, user_id: int, state: FSMContext = None):
    """Display question based on type and set appropriate FSM state."""
    logger.info(f"show_question: question_id={question.id}, type={question.question_type}, has_state={state is not None}")
    if question.question_type == "text":
        if state:
            await state.set_state(SurveyStates.waiting_for_answer)
            logger.info(f"Set state to waiting_for_answer for text question")
        await message.answer(
            f"❓ {question.question_text}\n\n"
            "Введите ваш ответ:",
            reply_markup=build_cancel_keyboard()
        )

    elif question.question_type == "single_choice":
        if state:
            await state.set_state(SurveyStates.waiting_for_answer)
            logger.info(f"Set state to waiting_for_answer for single_choice question")
        options_list = [
            {"id": opt.id, "option_text": opt.option_text}
            for opt in question.options
        ]
        keyboard = build_single_choice_keyboard(options_list)
        await message.answer(
            f"❓ {question.question_text}",
            reply_markup=keyboard
        )

    elif question.question_type == "multiple_choice":
        if state:
            await state.set_state(SurveyStates.selecting_options)
            # Reset selected answers for new question
            await state.update_data(selected_answers=[])
            logger.info(f"Set state to selecting_options for multiple_choice question")
        options_list = [
            {"id": opt.id, "option_text": opt.option_text}
            for opt in question.options
        ]
        keyboard = build_multiple_choice_keyboard(options_list)
        await message.answer(
            f"❓ {question.question_text}\n\n"
            "Выберите несколько вариантов:",
            reply_markup=keyboard
        )


@router.message(SurveyStates.waiting_for_answer)
async def handle_text_answer(message: Message, state: FSMContext):
    """Handle free text answers."""
    telegram_id = message.from_user.id

    async with async_session() as db:
        # Get current state data
        state_data = await state.get_data()
        survey_id = state_data.get("survey_id")
        response_id = state_data.get("response_id")
        current_question_index = state_data.get("current_question_index", 0)

        if not survey_id or not response_id:
            logger.error("Missing survey or response data in FSM")
            await message.answer("Ошибка: данные опроса не найдены. Пожалуйста, начните опрос заново.")
            return

        # Get survey with questions
        survey_result = await db.execute(
            select(Survey)
            .where(Survey.id == survey_id)
            .options(selectinload(Survey.questions).selectinload(Question.options))
        )
        survey = survey_result.scalar_one_or_none()

        if not survey or current_question_index >= len(survey.questions):
            logger.error(f"Invalid question index: {current_question_index}")
            await message.answer("Ошибка: вопрос не найден.")
            return

        question = survey.questions[current_question_index]

        # Validate answer (text questions always require an answer)
        if not message.text or not message.text.strip():
            await message.answer("Пожалуйста, введите ответ.")
            return

        # Save answer to database
        answer = Answer(
            question_id=question.id,
            response_id=response_id,
            answer_text=message.text.strip()
        )
        db.add(answer)

        # Update current question index
        new_index = current_question_index + 1
        await state.update_data(current_question_index=new_index)

        # Check if this was the last question
        if new_index >= len(survey.questions):
            # Complete survey
            await complete_survey(db, response_id)
            await state.clear()
            await message.answer(
                "✅ Опрос успешно завершен!\n\n"
                "Спасибо за участие в опросе.",
                reply_markup=build_help_keyboard()
            )
        else:
            # Show next question
            next_question = survey.questions[new_index]
            await show_question(message, next_question, message.bot, telegram_id, state)

        await db.commit()


@router.callback_query(SurveyStates.waiting_for_answer, F.data.startswith("option_"))
async def handle_single_choice(callback: CallbackQuery, state: FSMContext):
    """Handle single choice selection."""
    logger.info(f"handle_single_choice called: data={callback.data}, state={await state.get_state()}")
    telegram_id = callback.from_user.id

    async with async_session() as db:
        # Get current state data
        state_data = await state.get_data()
        survey_id = state_data.get("survey_id")
        response_id = state_data.get("response_id")
        current_question_index = state_data.get("current_question_index", 0)

        if not survey_id or not response_id:
            logger.error("Missing survey or response data in FSM")
            await callback.message.edit_text("Ошибка: данные опроса не найдены. Пожалуйста, начните опрос заново.")
            await callback.answer()
            return

        # Get survey with questions
        survey_result = await db.execute(
            select(Survey)
            .where(Survey.id == survey_id)
            .options(selectinload(Survey.questions).selectinload(Question.options))
        )
        survey = survey_result.scalar_one_or_none()

        if not survey or current_question_index >= len(survey.questions):
            logger.error(f"Invalid question index: {current_question_index}")
            await callback.message.edit_text("Ошибка: вопрос не найден.")
            await callback.answer()
            return

        question = survey.questions[current_question_index]
        option_id = int(callback.data.split("_")[1])

        # Validate option exists
        option = None
        for opt in question.options:
            if opt.id == option_id:
                option = opt
                break

        if not option:
            logger.error(f"Option not found: {option_id}")
            await callback.message.edit_text("Ошибка: вариант ответа не найден.")
            await callback.answer()
            return

        # Save answer to database
        answer = Answer(
            question_id=question.id,
            response_id=response_id,
            option_id=option.id
        )
        db.add(answer)

        # Update current question index
        new_index = current_question_index + 1
        await state.update_data(current_question_index=new_index)

        # Check if this was the last question
        if new_index >= len(survey.questions):
            # Complete survey
            await complete_survey(db, response_id)
            await state.clear()
            await callback.message.edit_text(
                "✅ Опрос успешно завершен!\n\n"
                "Спасибо за участие в опросе.",
                reply_markup=build_help_keyboard()
            )
        else:
            # Show next question
            next_question = survey.questions[new_index]
            await show_question(callback.message, next_question, callback.message.bot, telegram_id, state)

        await db.commit()
        await callback.answer()


@router.callback_query(SurveyStates.selecting_options, F.data.startswith("toggle_option_"))
async def toggle_option(callback: CallbackQuery, state: FSMContext):
    """Toggle option selection for multiple choice."""
    telegram_id = callback.from_user.id

    option_id = int(callback.data.split("_")[2])

    # Get current state data
    state_data = await state.get_data()
    current_question_index = state_data.get("current_question_index", 0)

    # Get selected options
    selected_answers = state_data.get("selected_answers", [])
    if option_id in selected_answers:
        selected_answers.remove(option_id)
    else:
        selected_answers.append(option_id)

    # Update state
    await state.update_data(selected_answers=selected_answers)

    # Get survey with questions
    async with async_session() as db:
        survey_id = state_data.get("survey_id")
        if not survey_id:
            await callback.answer(f"Toggled option {option_id}")
            return

        survey_result = await db.execute(
            select(Survey)
            .where(Survey.id == survey_id)
            .options(selectinload(Survey.questions).selectinload(Question.options))
        )
        survey = survey_result.scalar_one_or_none()

        if not survey:
            await callback.answer(f"Toggled option {option_id}")
            return

        question = survey.questions[current_question_index]

        # Rebuild keyboard with updated selection
        options_list = [
            {"id": opt.id, "option_text": opt.option_text}
            for opt in question.options
        ]
        keyboard = build_multiple_choice_keyboard(options_list, selected_answers)

        # Update message
        await callback.message.edit_text(
            f"❓ {question.question_text}\n\n"
            "Выберите несколько вариантов:",
            reply_markup=keyboard
        )

        await callback.answer()


@router.callback_query(SurveyStates.selecting_options, F.data == "submit_options")
async def submit_multiple_choice(callback: CallbackQuery, state: FSMContext):
    """Submit multiple choice selections."""
    telegram_id = callback.from_user.id

    async with async_session() as db:
        # Get current state data
        state_data = await state.get_data()
        survey_id = state_data.get("survey_id")
        response_id = state_data.get("response_id")
        current_question_index = state_data.get("current_question_index", 0)
        selected_answers = state_data.get("selected_answers", [])

        if not survey_id or not response_id:
            logger.error("Missing survey or response data in FSM")
            await callback.message.edit_text("Ошибка: данные опроса не найдены. Пожалуйста, начните опрос заново.")
            await callback.answer()
            return

        # Get survey with questions
        survey_result = await db.execute(
            select(Survey)
            .where(Survey.id == survey_id)
            .options(selectinload(Survey.questions).selectinload(Question.options))
        )
        survey = survey_result.scalar_one_or_none()

        if not survey or current_question_index >= len(survey.questions):
            logger.error(f"Invalid question index: {current_question_index}")
            await callback.message.edit_text("Ошибка: вопрос не найден.")
            await callback.answer()
            return

        question = survey.questions[current_question_index]

        # Validate that at least one option is selected
        if not selected_answers:
            await callback.message.edit_text(
                f"❓ {question.question_text}\n\n"
                "Пожалуйста, выберите хотя бы один вариант ответа.",
                reply_markup=build_multiple_choice_keyboard(
                    [{"id": opt.id, "option_text": opt.option_text} for opt in question.options],
                    selected_answers
                )
            )
            await callback.answer()
            return

        # Save answers to database
        for option_id in selected_answers:
            answer = Answer(
                question_id=question.id,
                response_id=response_id,
                option_id=option_id
            )
            db.add(answer)

        # Update current question index
        new_index = current_question_index + 1
        await state.update_data(current_question_index=new_index)

        # Check if this was the last question
        if new_index >= len(survey.questions):
            # Complete survey
            await complete_survey(db, response_id)
            await state.clear()
            await callback.message.edit_text(
                "✅ Опрос успешно завершен!\n\n"
                "Спасибо за участие в опросе.",
                reply_markup=build_help_keyboard()
            )
        else:
            # Show next question
            next_question = survey.questions[new_index]
            await show_question(callback.message, next_question, callback.message.bot, telegram_id, state)

        await db.commit()
        await callback.answer()


async def complete_survey(db: AsyncSession, response_id: int):
    """Complete survey by updating status and completed_at."""
    try:
        response = await db.get(SurveyResponse, response_id)
        if response:
            response.status = "completed"
            response.completed_at = datetime.utcnow()

            # Get employee and survey information
            employee_result = await db.execute(
                select(Employee).where(Employee.id == response.employee_id)
            )
            employee = employee_result.scalar_one_or_none()

            if employee:
                survey_result = await db.execute(
                    select(Survey).where(Survey.id == response.survey_id)
                )
                survey = survey_result.scalar_one_or_none()

                if survey:
                    # Send notification to HR
                    notification_service = NotificationService(bot)
                    for hr_telegram_id in settings.hr_telegram_id_list:
                        await notification_service.send_survey_completion_notification(
                            hr_telegram_id=hr_telegram_id,
                            employee_name=f"{employee.first_name} {employee.last_name}",
                            survey_title=survey.title
                        )

                    logger.info(
                        f"Survey completed for response_id: {response_id}, "
                        f"employee: {employee.first_name} {employee.last_name}, "
                        f"survey: {survey.title}"
                    )
    except Exception as e:
        logger.error(f"Error completing survey: {e}", exc_info=True)


@router.callback_query(F.data == "cancel_survey")
async def cancel_survey(callback: CallbackQuery, state: FSMContext):
    """Cancel survey in progress."""
    telegram_id = callback.from_user.id

    state_data = await state.get_data()
    response_id = state_data.get("response_id")

    # Update response status to cancelled
    async with async_session() as db:
        if response_id:
            try:
                response = await db.get(SurveyResponse, response_id)
                if response:
                    response.status = "cancelled"
                    await db.commit()
                    logger.info(f"Survey cancelled for response_id: {response_id}")
            except Exception as e:
                logger.error(f"Error cancelling survey: {e}")

    # Clear FSM state
    await state.clear()

    # Show cancel confirmation
    await callback.message.edit_text(
        "❌ Опрос отменен\n\n"
        "Вы можете начать опрос снова, когда он будет доступен.",
        reply_markup=build_help_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "my_surveys")
async def show_my_surveys(callback: CallbackQuery):
    """Show list of available surveys."""
    telegram_id = callback.from_user.id

    async with async_session() as db:
        # Get employee
        emp_result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = emp_result.scalar_one_or_none()

        if not employee:
            logger.warning(f"Employee not found for telegram_id: {telegram_id}")
            await callback.message.edit_text("Сотрудник не найден. Пожалуйста, свяжитесь с HR.")
            await callback.answer()
            return

        # Get active surveys
        result = await db.execute(
            select(Survey).where(Survey.is_active == True)
        )
        surveys = result.scalars().all()

        if not surveys:
            await callback.message.edit_text(
                "📋 Доступные опросы\n\n"
                "В данный момент нет доступных опросов.",
                reply_markup=build_help_keyboard()
            )
            await callback.answer()
            return

        # Build keyboard with surveys
        buttons = []
        for survey in surveys:
            buttons.append([
                InlineKeyboardButton(
                    text=survey.title,
                    callback_data=f"start_survey_{survey.id}"
                )
            ])

        # Add back button
        buttons.append([
            InlineKeyboardButton(text="← Назад", callback_data="back_to_menu")
        ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.edit_text(
            "📋 Доступные опросы\n\n"
            "Выберите опрос для прохождения:",
            reply_markup=keyboard
        )

        await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Show help information."""
    help_text = """🤖 Справка по HR Survey Bot

📋 **Как пройти опрос:**
1. Выберите доступный опрос из списка
2. Отвечайте на вопросы по порядку
3. Для текстовых вопросов введите ваш ответ
4. Для выбора вариантов нажмите на кнопку
5. Для множественного выбора выберите несколько вариантов и нажмите "✓ Submit"

❌ **Отмена опроса:**
- В любой момент нажмите "Отменить опрос"
- Опрос будет сохранен с статусом "cancelled"

📊 **Мои опросы:**
- Посмотрите список всех доступных опросов

Если у вас возникли вопросы, свяжитесь с HR."""
    
    await callback.message.edit_text(
        help_text,
        reply_markup=build_help_keyboard()
    )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Return to main menu."""
    telegram_id = callback.from_user.id

    async with async_session() as db:
        # Get employee
        emp_result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = emp_result.scalar_one_or_none()

        if not employee:
            await callback.message.edit_text("Сотрудник не найден. Пожалуйста, свяжитесь с HR.")
            await callback.answer()
            return

        # Check for pending surveys
        result = await db.execute(
            select(SurveyResponse).where(
                SurveyResponse.employee_id == employee.id,
                SurveyResponse.status.in_(["pending", "in_progress"])
            )
        )
        pending_responses = result.scalars().all()

        if pending_responses:
            await callback.message.edit_text(
                f"👋 Добро пожаловать, {employee.first_name}!\n\n"
                f"У вас {len(pending_responses)} опросов в ожидании. "
                f"Пожалуйста, проверьте меню для продолжения.",
                reply_markup=build_main_menu_keyboard()
            )
        else:
            await callback.message.edit_text(
                f"👋 Добро пожаловать, {employee.first_name}!\n\n"
                "Нет доступных опросов на данный момент. "
                "Вы будете notified, когда появятся новые опросы.",
                reply_markup=build_main_menu_keyboard()
            )

    await callback.answer()


# Debug handler - catch all callback queries with option_ prefix
@router.callback_query(F.data.startswith("option_"))
async def debug_option_handler(callback: CallbackQuery, state: FSMContext):
    """Debug handler for option callbacks."""
    current_state = await state.get_state()
    logger.warning(f"DEBUG: Received option callback: data={callback.data}, current_state={current_state}")
    await callback.answer("Debug: state check", show_alert=True)
