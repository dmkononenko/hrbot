from aiogram.fsm.state import State, StatesGroup


class SurveyStates(StatesGroup):
    """States for survey conversation flow."""

    waiting_for_answer = State()  # Waiting for answer to current question
    selecting_options = State()  # Selecting options (multiple choice)
    canceling_survey = State()  # User is canceling survey


class RegistrationStates(StatesGroup):
    """States for employee registration."""

    waiting_for_confirmation = State()  # Waiting for employee to confirm registration
