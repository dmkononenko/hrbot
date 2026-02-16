from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models import Employee, SurveyResponse
from app.bot.keyboards.keyboards import (
    build_main_menu_keyboard,
    build_help_keyboard,
    build_language_keyboard
)
from app.bot.helpers.localization import (
    LANG_KG,
    LANG_RU,
    get_welcome_message,
    get_help_message,
    get_message,
)
from datetime import datetime, timedelta

router = Router()


async def get_employee_language(employee: Employee) -> str:
    """Get employee language, default to 'ru' if not set."""
    return employee.language if employee.language else LANG_RU


async def show_language_selection(message: Message):
    """Show language selection keyboard."""
    await message.answer(
        "🌐 " + get_welcome_message(LANG_RU, "select_language"),
        reply_markup=build_language_keyboard()
    )


async def show_main_menu(message, employee: Employee, language: str):
    """Show main menu with localized content."""
    async with async_session() as db:
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

    await message.answer(text, reply_markup=build_main_menu_keyboard(language))


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command - auto-register new employees."""
    telegram_id = message.from_user.id
    user = message.from_user

    print(f"[DEBUG] /start received from telegram_id={telegram_id}, username={user.username}")

    async with async_session() as db:
        # Check if employee exists
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = result.scalar_one_or_none()

        # Auto-register new employee
        if not employee:
            new_employee = Employee(
                telegram_id=telegram_id,
                telegram_username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                start_date=datetime.now().date(),
                is_active=True,
            )
            db.add(new_employee)
            await db.commit()
            await db.refresh(new_employee)
            employee = new_employee

        # Check if language is set
        if not employee.language:
            await show_language_selection(message)
            return

        # Show main menu with employee's language
        await show_main_menu(message, employee, employee.language)


@router.callback_query(F.data.startswith("lang_"))
async def cmd_select_language(callback: CallbackQuery):
    """Handle language selection."""
    telegram_id = callback.from_user.id
    language = callback.data.split("_")[1]  # Extract 'kg' or 'ru'

    if language not in [LANG_KG, LANG_RU]:
        await callback.answer("❌ Invalid language selection")
        return

    async with async_session() as db:
        # Get employee
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            await callback.message.edit_text("❌ " + get_message(LANG_RU, "employee_not_found"))
            await callback.answer()
            return

        # Update employee language
        await db.execute(
            update(Employee).where(Employee.id == employee.id).values(language=language)
        )
        await db.commit()

        # Refresh employee object
        await db.refresh(employee)

    # Update the message with selected language confirmation
    lang_name = "Кыргызча" if language == LANG_KG else "Русский"
    await callback.message.edit_text(
        f"✅ Тил тандалды: {lang_name} / Язык выбран: {lang_name}\n\n"
        f"{get_welcome_message(language, 'greeting', name=employee.first_name or 'Кесиптеш')}\n\n"
        f"{get_welcome_message(language, 'intro')}\n\n"
        f"👇 Меню / Меню:",
        reply_markup=build_main_menu_keyboard(language)
    )

    await callback.answer()


@router.callback_query(F.data == "change_language")
async def cmd_change_language(callback: CallbackQuery):
    """Handle language change request."""
    telegram_id = callback.from_user.id

    async with async_session() as db:
        # Get employee
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == telegram_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            await callback.message.edit_text("❌ " + get_message(LANG_RU, "employee_not_found"))
            await callback.answer()
            return

    # Show language selection keyboard
    await callback.message.edit_text(
        "🌐 " + get_welcome_message(LANG_RU, "select_language"),
        reply_markup=build_language_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "help")
async def cmd_help(callback: CallbackQuery):
    """Show help information."""
    async with async_session() as db:
        # Get employee for language
        result = await db.execute(
            select(Employee).where(Employee.telegram_id == callback.from_user.id)
        )
        employee = result.scalar_one_or_none()
        language = await get_employee_language(employee) if employee else LANG_RU

    help_text = get_help_message(language)

    await callback.message.edit_text(
        help_text,
        reply_markup=build_help_keyboard(language)
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
            await callback.message.edit_text("❌ " + get_message(LANG_RU, "employee_not_found"))
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

        language = await get_employee_language(employee)
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
