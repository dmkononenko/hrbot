import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
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
    build_help_keyboard,
    build_main_menu_keyboard,
)
from app.bot.helpers.localization import (
    get_employee_language,
    get_message,
    get_help_message,
    get_welcome_message,
    LANG_KG,
    LANG_RU,
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
        language = get_employee_language(employee)

        if not employee:
            logger.warning(f"Employee not found for telegram_id: {telegram_id}")
            await callback.message.edit_text(get_message(language, "employee_not_found"))
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
            await callback.message.edit_text(get_message(language, "no_pending_survey"))
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
            await callback.message.edit_text(get_message(language, "survey_no_questions"))
            return

        # Store survey and response data in FSM
        await state.update_data(
            survey_id=survey_id,
            response_id=response.id,
            current_question_index=0,
            selected_answers=[],
            language=language,
        )
        logger.info(f"Stored FSM data for user {telegram_id}: survey_id={survey_id}, response_id={response.id}")

        # Show first question
        first_question = survey.questions[0]
        logger.info(f"About to show first question: id={first_question.id}, type={first_question.question_type}")
        await show_question(callback.message, first_question, callback.message.bot, callback.from_user.id, state)

        await callback.answer()


async def show_question(message: Message, question: Question, bot, user_id: int, state: FSMContext = None):
    """Display question based on type and set appropriate FSM state."""
    logger.info(f"show_question: question_id={question.id}, type={question.question_type}, has_state={state is not None}")

    # Get language from state
    language = LANG_RU
    if state:
        state_data = await state.get_data()
        language = state_data.get("language", LANG_RU)

    # Get localized question text
    question_text = question.question_text  # Default (RU)
    if language == LANG_KG and question.question_text_kg:
        question_text = question.question_text_kg

    if question.question_type == "text":
        if state:
            await state.set_state(SurveyStates.waiting_for_text_answer)
            logger.info(f"Set state to waiting_for_text_answer for text question, state={await state.get_state()}")
        await message.answer(
            f"❓ {question_text}\n\n"
            f"{get_message(language, 'enter_answer')}",
            reply_markup=build_cancel_keyboard(language)
        )
        logger.info(f"Sent text question message to user_id={user_id if user_id else 'unknown'}")

    elif question.question_type == "single_choice":
        if state:
            await state.set_state(SurveyStates.waiting_for_single_choice)
            new_state = await state.get_state()
            logger.info(f"[DEBUG] Set state to waiting_for_single_choice for single_choice question")
            logger.info(f"[DEBUG] State after set: {new_state}, state_type={type(new_state)}")
            # Verify state was saved
            state_data = await state.get_data()
            logger.info(f"[DEBUG] FSM data after state set: survey_id={state_data.get('survey_id')}, response_id={state_data.get('response_id')}")
        else:
            logger.warning(f"[DEBUG] State is None! Cannot set state for single_choice question")
        options_list = [
            {"id": opt.id, "option_text": opt.option_text}
            for opt in question.options
        ]
        logger.info(f"[DEBUG] Building single_choice keyboard with {len(options_list)} options")
        keyboard = build_single_choice_keyboard(options_list)
        await message.answer(
            f"❓ {question_text}",
            reply_markup=keyboard
        )
        logger.info(f"[DEBUG] Single choice question sent to user")

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
            f"❓ {question_text}\n\n"
            f"{get_message(language, 'select_multiple')}",
            reply_markup=keyboard
        )


@router.message(SurveyStates.waiting_for_text_answer)
async def handle_text_answer(message: Message, state: FSMContext):
    """Handle free text answers."""
    current_state = await state.get_state()
    logger.info(f"handle_text_answer called: text='{message.text}', state={current_state}, user_id={message.from_user.id}")

    telegram_id = message.from_user.id

    # Get language from state
    state_data = await state.get_data()
    logger.info(f"State data: {state_data}")
    language = state_data.get("language", LANG_RU)
    current_question_index = state_data.get("current_question_index", 0)
    survey_id = state_data.get("survey_id")
    response_id = state_data.get("response_id")

    if not survey_id or not response_id:
        logger.error(f"Missing survey_id or response_id in FSM state. survey_id={survey_id}, response_id={response_id}")
        await message.answer(get_message(language, "error_no_data"))
        await state.clear()
        return

    async with async_session() as db:
        # Get survey with questions
        survey_result = await db.execute(
            select(Survey)
            .where(Survey.id == survey_id)
            .options(selectinload(Survey.questions).selectinload(Question.options))
        )
        survey = survey_result.scalar_one_or_none()

        logger.info(f"DEBUG: survey_id={survey_id}, questions_count={len(survey.questions) if survey else 0}, current_index={current_question_index}")
        if survey:
            for i, q in enumerate(survey.questions):
                logger.info(f"  Question {i}: id={q.id}, type={q.question_type}")

        if not survey or current_question_index >= len(survey.questions):
            logger.error(f"Invalid question index: {current_question_index}, total: {len(survey.questions) if survey else 0}")
            await message.answer(get_message(language, "error_question_not_found"))
            await state.clear()
            return

        question = survey.questions[current_question_index]
        logger.info(f"Current question: id={question.id}, type={question.question_type}")

        # Validate answer (text questions always require an answer)
        if not message.text or not message.text.strip():
            logger.warning(f"Empty answer received from user {telegram_id}")
            await message.answer(get_message(language, "please_enter_answer"))
            return

        # Save answer to database
        answer = Answer(
            question_id=question.id,
            response_id=response_id,
            answer_text=message.text.strip()
        )
        db.add(answer)
        await db.commit()
        logger.info(f"Saved answer for question {question.id}, response_id={response_id}")

        # Update current question index
        new_index = current_question_index + 1
        await state.update_data(current_question_index=new_index)

        # Check if this was the last question
        if new_index >= len(survey.questions):
            # Complete survey
            await complete_survey(db, response_id)
            await state.clear()
            await message.answer(
                get_message(language, "survey_completed"),
                reply_markup=build_help_keyboard(language)
            )
        else:
            # Show next question
            next_question = survey.questions[new_index]
            await show_question(message, next_question, message.bot, telegram_id, state)


@router.callback_query(F.data.startswith("option_"))
async def handle_single_choice(callback: CallbackQuery, state: FSMContext):
    """Handle single choice selection."""
    current_state = await state.get_state()
    logger.info(f"[DEBUG] handle_single_choice called: data={callback.data}, state={current_state}, state_type={type(current_state)}")

    # Check if user is in the right state
    # In aiogram 3.x, get_state() returns a State object with .state attribute for string value
    current_state_str = current_state.state if current_state else None
    logger.info(f"[DEBUG] Current state string: {current_state_str}, expected: {SurveyStates.waiting_for_single_choice.state}")
    
    # DEBUG: Log all FSM data to understand the current state
    state_data = await state.get_data()
    logger.info(f"[DEBUG] FSM data: survey_id={state_data.get('survey_id')}, response_id={state_data.get('response_id')}, current_question_index={state_data.get('current_question_index')}")
    
    # Use endswith to handle @: prefix in state string
    expected_state = SurveyStates.waiting_for_single_choice.state
    if not current_state_str or not current_state_str.endswith(expected_state):
        logger.warning(f"[DEBUG] Wrong state for single choice: expected {expected_state}, got {current_state_str}")
        # DEBUG: Provide user feedback instead of silent failure
        language = state_data.get("language", LANG_RU)
        await callback.answer(get_message(language, "error_wrong_state") if language else "Ошибка состояния. Попробуйте начать опрос заново.", show_alert=True)
        return

    telegram_id = callback.from_user.id
    logger.info(f"Processing single choice for user {telegram_id}")

    # Get language from state
    state_data = await state.get_data()
    logger.info(f"Retrieved FSM data: survey_id={state_data.get('survey_id')}, response_id={state_data.get('response_id')}, current_question_index={state_data.get('current_question_index')}")
    language = state_data.get("language", LANG_RU)

    async with async_session() as db:
        # Get current state data
        survey_id = state_data.get("survey_id")
        response_id = state_data.get("response_id")
        current_question_index = state_data.get("current_question_index", 0)

        if not survey_id or not response_id:
            logger.error(f"Missing survey or response data in FSM. Got: survey_id={survey_id}, response_id={response_id}")
            await callback.message.edit_text(get_message(language, "error_no_data"))
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
            await callback.message.edit_text(get_message(language, "error_question_not_found"))
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
            await callback.message.edit_text(get_message(language, "error_option_not_found"))
            await callback.answer()
            return

        # Save answer to database
        logger.info(f"Saving answer: question_id={question.id}, response_id={response_id}, option_id={option.id}")
        answer = Answer(
            question_id=question.id,
            response_id=response_id,
            answer_options=[option.id]
        )
        db.add(answer)

        # Update current question index
        new_index = current_question_index + 1
        await state.update_data(current_question_index=new_index)
        logger.info(f"Updated question index from {current_question_index} to {new_index}")

        # Check if this was the last question
        if new_index >= len(survey.questions):
            # Complete survey
            logger.info(f"Last question reached, completing survey for response_id={response_id}")
            await complete_survey(db, response_id)
            await state.clear()
            await callback.message.edit_text(
                get_message(language, "survey_completed"),
                reply_markup=build_help_keyboard(language)
            )
        else:
            # Show next question
            next_question = survey.questions[new_index]
            logger.info(f"Moving to next question: index={new_index}, question_id={next_question.id}, type={next_question.question_type}")
            await show_question(callback.message, next_question, callback.message.bot, telegram_id, state)

        await db.commit()
        logger.info(f"Answer committed to database for question {question.id}")
        await callback.answer()


@router.callback_query(F.data.startswith("toggle_option_"))
async def toggle_option(callback: CallbackQuery, state: FSMContext):
    """Toggle option selection for multiple choice."""
    current_state = await state.get_state()
    current_state_str = current_state.state if current_state else None
    logger.info(f"toggle_option called: data={callback.data}, state={current_state_str}")
    
    # Use endswith to handle @: prefix in state string
    expected_state = SurveyStates.selecting_options.state
    if not current_state_str or not current_state_str.endswith(expected_state):
        logger.warning(f"Wrong state for toggle_option: expected {expected_state}, got {current_state_str}")
        await callback.answer()
        return

    telegram_id = callback.from_user.id
    option_id = int(callback.data.split("_")[2])
    logger.info(f"Toggling option {option_id} for user {telegram_id}")

    # Get current state data
    state_data = await state.get_data()
    current_question_index = state_data.get("current_question_index", 0)
    logger.info(f"Current question index: {current_question_index}")

    # Get selected options
    selected_answers = state_data.get("selected_answers", [])
    if option_id in selected_answers:
        selected_answers.remove(option_id)
        logger.info(f"Removed option {option_id} from selection")
    else:
        selected_answers.append(option_id)
        logger.info(f"Added option {option_id} to selection")

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

        # Get localized question text
        language = state_data.get("language", LANG_RU)
        question_text = question.question_text  # Default (RU)
        if language == LANG_KG and question.question_text_kg:
            question_text = question.question_text_kg

        # Rebuild keyboard with updated selection
        options_list = [
            {"id": opt.id, "option_text": opt.option_text}
            for opt in question.options
        ]
        keyboard = build_multiple_choice_keyboard(options_list, selected_answers)

        # Update message
        await callback.message.edit_text(
            f"❓ {question_text}\n\n"
            f"{get_message(language, 'select_multiple')}:",
            reply_markup=keyboard
        )

        await callback.answer()


@router.callback_query(F.data == "submit_options")
async def submit_multiple_choice(callback: CallbackQuery, state: FSMContext):
    """Submit multiple choice selections."""
    current_state = await state.get_state()
    current_state_str = current_state.state if current_state else None
    logger.info(f"submit_multiple_choice called: state={current_state_str}")
    
    # Use endswith to handle @: prefix in state string
    expected_state = SurveyStates.selecting_options.state
    if not current_state_str or not current_state_str.endswith(expected_state):
        logger.warning(f"Wrong state for submit_multiple_choice: expected {expected_state}, got {current_state_str}")
        await callback.answer()
        return

    telegram_id = callback.from_user.id
    logger.info(f"Submitting multiple choice for user {telegram_id}")

    # Get language from state
    state_data = await state.get_data()
    logger.info(f"Retrieved FSM data: survey_id={state_data.get('survey_id')}, response_id={state_data.get('response_id')}, current_question_index={state_data.get('current_question_index')}, selected_answers={state_data.get('selected_answers')}")
    language = state_data.get("language", LANG_RU)

    async with async_session() as db:
        # Get current state data
        survey_id = state_data.get("survey_id")
        response_id = state_data.get("response_id")
        current_question_index = state_data.get("current_question_index", 0)
        selected_answers = state_data.get("selected_answers", [])

        if not survey_id or not response_id:
            logger.error("Missing survey or response data in FSM")
            await callback.message.edit_text(get_message(language, "error_no_data"))
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
            await callback.message.edit_text(get_message(language, "error_question_not_found"))
            await callback.answer()
            return

        question = survey.questions[current_question_index]

        # Get localized question text
        question_text = question.question_text  # Default (RU)
        if language == LANG_KG and question.question_text_kg:
            question_text = question.question_text_kg

        # Validate that at least one option is selected
        if not selected_answers:
            await callback.message.edit_text(
                f"❓ {question_text}\n\n"
                f"{get_message(language, 'select_at_least_one')}",
                reply_markup=build_multiple_choice_keyboard(
                    [{"id": opt.id, "option_text": opt.option_text} for opt in question.options],
                    selected_answers
                )
            )
            await callback.answer()
            return

        # Save answers to database (as JSON array)
        answer = Answer(
            question_id=question.id,
            response_id=response_id,
            answer_options=selected_answers
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
                get_message(language, "survey_completed"),
                reply_markup=build_help_keyboard(language)
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

    # Get language from state
    state_data = await state.get_data()
    language = state_data.get("language", LANG_RU)
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
        get_message(language, "survey_cancelled"),
        reply_markup=build_help_keyboard(language)
    )

    await callback.answer()


@router.callback_query(F.data == "my_surveys")
async def show_my_surveys(callback: CallbackQuery):
    """Show list of available surveys assigned to the employee."""
    telegram_id = callback.from_user.id

    async with async_session() as db:
        # Get employee
        emp_result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = emp_result.scalar_one_or_none()
        language = get_employee_language(employee)

        if not employee:
            logger.warning(f"Employee not found for telegram_id: {telegram_id}")
            await callback.message.edit_text(get_message(language, "employee_not_found"))
            await callback.answer()
            return

        # Get survey responses for this employee (pending or in_progress)
        result = await db.execute(
            select(SurveyResponse)
            .where(
                SurveyResponse.employee_id == employee.id,
                SurveyResponse.status.in_(["pending", "in_progress"])
            )
            .options(selectinload(SurveyResponse.survey))
        )
        responses = result.scalars().all()

        if not responses:
            await callback.message.edit_text(
                get_message(language, "no_surveys"),
                reply_markup=build_help_keyboard(language)
            )
            await callback.answer()
            return

        # Build keyboard with assigned surveys
        buttons = []
        for response in responses:
            survey = response.survey
            if survey and survey.is_active:
                status_emoji = "⏳" if response.status == "pending" else "🔄"
                buttons.append([
                    InlineKeyboardButton(
                        text=f"{status_emoji} {survey.title}",
                        callback_data=f"start_survey_{survey.id}"
                    )
                ])

        if not buttons:
            await callback.message.edit_text(
                get_message(language, "no_surveys"),
                reply_markup=build_help_keyboard(language)
            )
            await callback.answer()
            return

        # Add back button
        back_text = get_message(language, "back")
        buttons.append([
            InlineKeyboardButton(text=back_text, callback_data="back_to_menu")
        ])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await callback.message.edit_text(
            get_message(language, "select_survey"),
            reply_markup=keyboard
        )

        await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Show help information."""
    async with async_session() as db:
        # Get employee for language
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == callback.from_user.id)
        )
        employee = result.scalar_one_or_none()
        language = get_employee_language(employee)

    help_text = get_help_message(language)

    await callback.message.edit_text(
        help_text,
        reply_markup=build_help_keyboard(language)
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
        language = get_employee_language(employee)

        if not employee:
            await callback.message.edit_text(get_message(language, "employee_not_found"))
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

        name = employee.first_name or "Кесиптеш"

        if pending_responses:
            text = (
                f"👋 {get_welcome_message(language, 'greeting', name=name)}\n\n"
                f"{get_welcome_message(language, 'intro')}\n\n"
                f"{get_welcome_message(language, 'pending_surveys', count=len(pending_responses))}"
            )
        else:
            text = (
                f"👋 {get_welcome_message(language, 'greeting', name=name)}\n\n"
                f"{get_welcome_message(language, 'intro')}\n\n"
                f"{get_welcome_message(language, 'no_surveys')}"
            )

        await callback.message.edit_text(
            text,
            reply_markup=build_main_menu_keyboard(language)
        )

    await callback.answer()


