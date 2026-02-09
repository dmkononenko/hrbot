from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List

from app.database import get_db
from app.models import Employee, Survey, SurveyResponse, Question
from app.config import settings
from app.bot.bot import bot
from app.bot.services.notification_service import NotificationService

router = APIRouter()


class InitiateSurveyRequest(BaseModel):
    employee_telegram_id: int
    survey_id: int


class WebhookResponse(BaseModel):
    status: str


@router.post("/webhook", response_model=WebhookResponse)
async def bot_webhook(request: Request):
    """
    Telegram webhook endpoint.
    Updates from Telegram are forwarded to the Aiogram dispatcher.
    This is a placeholder - actual webhook handling is done in main.py
    """
    # The actual webhook processing is handled by Aiogram dispatcher
    # This endpoint exists for OpenAPI documentation
    return {"status": "ok"}


@router.post("/initiate-survey")
async def initiate_survey(
    request: InitiateSurveyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    HR initiates a survey for an employee.
    Checks if employee is eligible (90+ days after start date).
    """
    # Get employee
    employee_result = await db.execute(
        select(Employee).where(Employee.telegram_id == request.employee_telegram_id)
    )
    employee = employee_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Get survey
    survey_result = await db.execute(
        select(Survey).where(Survey.id == request.survey_id)
    )
    survey = survey_result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    if not survey.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey is not active"
        )

    # Check 90-day eligibility
    days_since_start = (datetime.now().date() - employee.start_date).days
    if days_since_start < survey.days_after_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee has only been with us for {days_since_start} days. "
                   f"Surveys can be initiated after {survey.days_after_start} days."
        )

    # Check if response already exists
    existing_result = await db.execute(
        select(SurveyResponse).where(
            SurveyResponse.survey_id == request.survey_id,
            SurveyResponse.employee_id == employee.id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey response already exists for this employee"
        )

    # Create survey response
    db_response = SurveyResponse(
        survey_id=request.survey_id,
        employee_id=employee.id,
        status="pending"
    )
    db.add(db_response)
    await db.commit()
    await db.refresh(db_response)

    # Отправляем приглашение на опрос
    invite_result = await notification_service.send_survey_invite(
        employee_id=employee.id,
        survey_id=request.survey_id,
        db=db
    )

    return {
        "message": "Survey initiated successfully",
        "response_id": db_response.id,
        "employee_telegram_id": employee.telegram_id,
        "survey_id": survey.id,
        "invite_sent": invite_result["success"],
        "invite_error": invite_result.get("error") if not invite_result["success"] else None
    }


# Инициализация сервиса уведомлений
notification_service = NotificationService(bot)


@router.post("/send-invite")
async def send_survey_invite(
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Отправка приглашения на прохождение опроса сотруднику.
    """
    result = await notification_service.send_survey_invite(
        employee_id=request["employee_id"],
        survey_id=request["survey_id"],
        db=db
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to send invite")
        )

    return result


@router.post("/send-reminder")
async def send_survey_reminder(
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Отправка напоминания о прохождении опроса.
    """
    result = await notification_service.send_reminder(
        employee_id=request["employee_id"],
        survey_id=request["survey_id"],
        db=db,
        days_remaining=request.get("days_remaining")
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to send reminder")
        )

    return result


@router.post("/send-reminders-batch")
async def send_reminders_batch(
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Отправка серии напоминаний всем сотрудникам, у которых есть опрос.
    """
    result = await notification_service.send_multiple_reminders(
        survey_id=request["survey_id"],
        db=db,
        days=request.get("days", [3, 1, 0])
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to send reminders")
        )

    return result


@router.get("/surveys/{telegram_id}")
async def get_user_surveys(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получение списка доступных опросов для пользователя.
    """
    # Получаем сотрудника
    employee_result = await db.execute(
        select(Employee).where(Employee.telegram_id == telegram_id)
    )
    employee = employee_result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Получаем все активные опросы
    surveys_result = await db.execute(
        select(Survey).where(Survey.is_active == True)
    )
    surveys = surveys_result.scalars().all()

    # Фильтруем опросы, для которых еще нет ответа у сотрудника
    available_surveys = []
    for survey in surveys:
        # Проверяем, есть ли уже ответ
        existing_result = await db.execute(
            select(SurveyResponse).where(
                SurveyResponse.survey_id == survey.id,
                SurveyResponse.employee_id == employee.id
            )
        )
        existing = existing_result.scalar_one_or_none()

        if not existing:
            # Получаем количество вопросов
            questions_result = await db.execute(
                select(Question).where(Question.survey_id == survey.id)
            )
            questions = questions_result.scalars().all()

            available_surveys.append({
                "id": survey.id,
                "title": survey.title,
                "description": survey.description,
                "is_active": survey.is_active,
                "days_after_start": survey.days_after_start,
                "questions_count": len(questions)
            })

    return {
        "telegram_id": telegram_id,
        "surveys": available_surveys,
        "total": len(available_surveys)
    }


@router.get("/eligible-employees/{survey_id}")
async def get_eligible_employees(
    survey_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get list of employees eligible for a survey (90+ days after start)."""
    # Get survey
    survey_result = await db.execute(select(Survey).where(Survey.id == survey_id))
    survey = survey_result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    # Get eligible employees
    cutoff_date = datetime.now().date() - timedelta(days=survey.days_after_start)

    result = await db.execute(
        select(Employee).where(
            Employee.start_date <= cutoff_date,
            Employee.is_active == True
        )
    )
    employees = result.scalars().all()

    return {
        "survey_id": survey_id,
        "days_after_start": survey.days_after_start,
        "eligible_employees": [
            {
                "id": emp.id,
                "telegram_id": emp.telegram_id,
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "start_date": emp.start_date,
                "days_since_start": (datetime.now().date() - emp.start_date).days,
            }
            for emp in employees
        ],
        "total": len(employees),
    }
