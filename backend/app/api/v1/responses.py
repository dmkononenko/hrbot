from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models import SurveyResponse, Answer, Survey, Question, QuestionOption, Employee
from app.schemas import ResponseList, SurveyResults, ResponseResult, QuestionResult, EmployeeResult

router = APIRouter()


@router.get("", response_model=ResponseList)
async def get_responses(
    skip: int = 0,
    limit: int = 100,
    survey_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Get list of all responses."""
    query = select(SurveyResponse).options(selectinload(SurveyResponse.answers))

    if survey_id:
        query = query.where(SurveyResponse.survey_id == survey_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    responses = result.scalars().all()

    # Get total count
    count_query = select(SurveyResponse)
    if survey_id:
        count_query = count_query.where(SurveyResponse.survey_id == survey_id)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    return ResponseList(responses=responses, total=total)


@router.get("/surveys/{survey_id}/results", response_model=SurveyResults)
async def get_survey_results(survey_id: int, db: AsyncSession = Depends(get_db)):
    """Get survey results in JSON format."""
    # Get survey
    survey_result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .options(selectinload(Survey.questions).selectinload(Question.options))
    )
    survey = survey_result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    # Get all responses with answers and employee
    responses_result = await db.execute(
        select(SurveyResponse)
        .where(SurveyResponse.survey_id == survey_id)
        .options(
            selectinload(SurveyResponse.answers),
            selectinload(SurveyResponse.employee)
        )
    )
    responses = responses_result.scalars().all()

    # Get total eligible employees (active employees who started 90+ days ago)
    from datetime import datetime, timedelta
    ninety_days_ago = datetime.now().date() - timedelta(days=survey.days_after_start)

    eligible_result = await db.execute(
        select(func.count(Employee.id))
        .where(Employee.start_date <= ninety_days_ago)
        .where(Employee.is_active == True)
    )
    eligible_count = eligible_result.scalar() or 0

    # Build response results
    response_results = []
    for response in responses:
        employee = response.employee

        # Build employee result
        employee_result = EmployeeResult(
            id=employee.id,
            telegram_id=employee.telegram_id,
            telegram_username=employee.telegram_username,
            first_name=employee.first_name,
            last_name=employee.last_name,
        )

        # Build question results
        question_results = []
        for answer in response.answers:
            # Find question
            question = next((q for q in survey.questions if q.id == answer.question_id), None)
            if not question:
                continue

            # Get option texts for choice answers
            answer_options_texts = None
            if answer.answer_options:
                answer_options_texts = []
                for option_id in answer.answer_options:
                    option = next((o for o in question.options if o.id == option_id), None)
                    if option:
                        answer_options_texts.append(option.option_text)

            question_result = QuestionResult(
                question_id=answer.question_id,
                question_text=question.question_text,
                question_type=question.question_type,
                answer_text=answer.answer_text,
                answer_options=answer_options_texts,
            )
            question_results.append(question_result)

        response_result = ResponseResult(
            response_id=response.id,
            employee=employee_result,
            completed_at=response.completed_at,
            answers=question_results,
        )
        response_results.append(response_result)

    # Calculate completion rate
    completion_rate = 0.0
    if eligible_count > 0:
        completion_rate = len([r for r in response_results if r.completed_at]) / eligible_count

    return SurveyResults(
        survey_id=survey.id,
        survey_title=survey.title,
        responses=response_results,
        total_responses=len(response_results),
        completion_rate=completion_rate,
    )


@router.get("/{response_id}", response_model=SurveyResponse)
async def get_response(response_id: int, db: AsyncSession = Depends(get_db)):
    """Get response by ID."""
    result = await db.execute(
        select(SurveyResponse)
        .where(SurveyResponse.id == response_id)
        .options(selectinload(SurveyResponse.answers))
    )
    response = result.scalar_one_or_none()

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )

    return response
