"""
Pydantic схемы для API уведомлений Telegram бота.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SurveyInviteRequest(BaseModel):
    """Запрос на отправку приглашения на опрос."""
    employee_id: int = Field(..., description="ID сотрудника")
    survey_id: int = Field(..., description="ID опроса")


class SurveyReminderRequest(BaseModel):
    """Запрос на отправку напоминания."""
    employee_id: int = Field(..., description="ID сотрудника")
    survey_id: int = Field(..., description="ID опроса")
    days_remaining: Optional[int] = Field(
        None,
        description="Количество дней до дедлайна (опционально)"
    )


class SurveyListResponse(BaseModel):
    """Ответ с списком опросов для пользователя."""
    surveys: List[dict] = Field(..., description="Список доступных опросов")
    total: int = Field(..., description="Общее количество опросов")


class SurveyItem(BaseModel):
    """Элемент списка опросов."""
    id: int
    title: str
    description: Optional[str]
    is_active: bool
    days_after_start: int
    questions_count: int = Field(..., description="Количество вопросов в опросе")


class NotificationResult(BaseModel):
    """Результат отправки уведомления."""
    success: bool
    employee_telegram_id: Optional[int] = None
    survey_title: Optional[str] = None
    message_id: Optional[int] = None
    error: Optional[str] = None


class MultiReminderResult(BaseModel):
    """Результат отправки серии напоминаний."""
    success: bool
    total_sent: int
    results: List[dict]


class SendReminderBatchRequest(BaseModel):
    """Запрос на отправку напоминаний всем сотрудникам."""
    survey_id: int = Field(..., description="ID опроса")
    days: List[int] = Field(
        default=[3, 1, 0],
        description="Список дней до дедлайна для отправки напоминаний"
    )
