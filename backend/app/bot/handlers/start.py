from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models import Employee, SurveyResponse
from app.bot.keyboards.keyboards import build_main_menu_keyboard, build_help_keyboard
from datetime import datetime, timedelta

router = Router()


async def get_db_session() -> AsyncSession:
    """Get database session."""
    async with async_session() as session:
        yield session


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    telegram_id = message.from_user.id

    async with async_session() as db:
        # Check if employee exists
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            await message.answer(
                "👋 Welcome to the HR Survey Bot!\n\n"
                "You're not registered in our system yet. "
                "Please contact HR to complete your registration."
            )
            return

        # Check for pending surveys
        cutoff_date = datetime.now().date() - timedelta(days=90)

        # Get active surveys the employee is eligible for
        result = await db.execute(
            select(SurveyResponse).where(
                SurveyResponse.employee_id == employee.id,
                SurveyResponse.status.in_(["pending", "in_progress"])
            )
        )
        pending_responses = result.scalars().all()

        if pending_responses:
            await message.answer(
                f"👋 Welcome back, {employee.first_name}!\n\n"
                f"You have {len(pending_responses)} pending survey(s). "
                f"Please check the main menu to continue.",
                reply_markup=build_main_menu_keyboard()
            )
        else:
            await message.answer(
                f"👋 Добро пожаловать, {employee.first_name}!\n\n"
                "В данный момент нет доступных опросов. "
                "Вы будете notified, когда появятся новые опросы.",
                reply_markup=build_main_menu_keyboard()
            )


@router.callback_query(F.data == "help")
async def cmd_help(callback: CallbackQuery):
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
async def cmd_back_to_menu(callback: CallbackQuery):
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
