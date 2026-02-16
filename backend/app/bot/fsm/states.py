from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    """States for survey conversation flow."""

    waiting_for_text_answer = State()  # Waiting for text answer
    waiting_for_single_choice = State()  # Waiting for single choice selection
    selecting_options = State()  # Selecting options (multiple choice)
    canceling_survey = State()  # User is canceling survey


class RegistrationStates(StatesGroup):
    """States for employee registration."""

    waiting_for_confirmation = State()  # Waiting for employee to confirm registration
