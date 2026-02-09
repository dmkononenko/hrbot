from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def build_single_choice_keyboard(options: List[dict], selected_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for single choice questions."""
    buttons = []
    for option in options:
        is_selected = selected_id == option["id"]
        text = f"✓ {option['option_text']}" if is_selected else option["option_text"]
        buttons.append([
            InlineKeyboardButton(text=text, callback_data=f"option_{option['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_multiple_choice_keyboard(options: List[dict], selected_ids: Optional[List[int]] = None) -> InlineKeyboardMarkup:
    """Build inline keyboard for multiple choice questions."""
    selected_ids = selected_ids or []
    buttons = []
    for option in options:
        is_selected = option["id"] in selected_ids
        text = f"☑ {option['option_text']}" if is_selected else f"☐ {option['option_text']}"
        buttons.append([
            InlineKeyboardButton(text=text, callback_data=f"toggle_option_{option['id']}")
        ])

    # Add submit button
    buttons.append([
        InlineKeyboardButton(text="✓ Submit", callback_data="submit_options")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_survey_list_keyboard(surveys: List[dict]) -> InlineKeyboardMarkup:
    """Build keyboard with available surveys."""
    buttons = []
    for survey in surveys:
        buttons.append([
            InlineKeyboardButton(
                text=survey["title"],
                callback_data=f"start_survey_{survey['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build main menu keyboard."""
    buttons = [
        [InlineKeyboardButton(text="Мои опросы", callback_data="my_surveys")],
        [InlineKeyboardButton(text="Справка", callback_data="help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_cancel_keyboard() -> InlineKeyboardMarkup:
    """Build keyboard with cancel button."""
    buttons = [
        [InlineKeyboardButton(text="❌ Отменить опрос", callback_data="cancel_survey")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_help_keyboard() -> InlineKeyboardMarkup:
    """Build help keyboard."""
    buttons = [
        [InlineKeyboardButton(text="← Назад", callback_data="back_to_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
