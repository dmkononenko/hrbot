from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any


class AnswerBase(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    answer_options: Optional[List[int]] = None


class AnswerCreate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int
    response_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SurveyResponseBase(BaseModel):
    survey_id: int
    employee_id: int
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed)$")


class SurveyResponseCreate(SurveyResponseBase):
    pass


class SurveyResponse(SurveyResponseBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    answers: List[Answer] = []

    class Config:
        from_attributes = True


# Result schemas for API
class QuestionResult(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    answer_text: Optional[str] = None
    answer_options: Optional[List[str]] = None  # Option texts, not IDs


class EmployeeResult(BaseModel):
    id: int
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ResponseResult(BaseModel):
    response_id: int
    employee: EmployeeResult
    completed_at: Optional[datetime] = None
    answers: List[QuestionResult]


class SurveyResults(BaseModel):
    survey_id: int
    survey_title: str
    responses: List[ResponseResult]
    total_responses: int
    completion_rate: float


class ResponseList(BaseModel):
    responses: List[SurveyResponse]
    total: int


# Analytics schemas
class QuestionAnalytics(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    total_answers: int
    choice_distribution: Optional[List[dict]] = None  # For choice questions: [{"option": "text", "count": 5, "percentage": 25.0}]
    text_responses: Optional[List[str]] = None  # For text questions


class SurveyAnalytics(BaseModel):
    survey_id: int
    survey_title: str
    total_responses: int
    completed_responses: int
    completion_rate: float
    question_analytics: List[QuestionAnalytics]
