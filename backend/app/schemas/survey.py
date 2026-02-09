from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# Question Option Schemas
class QuestionOptionBase(BaseModel):
    option_text: str = Field(..., max_length=255)
    order_index: int = 0


class QuestionOptionCreate(QuestionOptionBase):
    pass


class QuestionOption(QuestionOptionBase):
    id: int

    class Config:
        from_attributes = True


# Question Schemas
class QuestionBase(BaseModel):
    question_text: str = Field(..., description="The question text")
    question_type: str = Field(..., pattern="^(text|single_choice|multiple_choice)$")
    order_index: int = 0
    is_required: bool = True


class QuestionCreate(QuestionBase):
    options: Optional[List[QuestionOptionCreate]] = []


class Question(QuestionBase):
    id: int
    survey_id: int
    options: List[QuestionOption] = []

    class Config:
        from_attributes = True


# Survey Schemas
class SurveyBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    days_after_start: int = Field(default=90, ge=1)
    is_active: bool = True


class SurveyCreate(SurveyBase):
    questions: Optional[List[QuestionCreate]] = []


class SurveyUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    days_after_start: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    questions: Optional[List[QuestionCreate]] = None


class Survey(SurveyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    questions: List[Question] = []

    class Config:
        from_attributes = True


class SurveyList(BaseModel):
    surveys: List[Survey]
    total: int
