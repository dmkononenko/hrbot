from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models import Survey, Question, QuestionOption
from app.schemas import SurveyCreate, SurveyUpdate, Survey as SurveySchema, SurveyList

router = APIRouter()


@router.get("", response_model=SurveyList)
async def get_surveys(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get list of all surveys."""
    query = select(Survey)
    if active_only:
        query = query.where(Survey.is_active == True)

    query = query.offset(skip).limit(limit).options(selectinload(Survey.questions).selectinload(Question.options))
    result = await db.execute(query)
    surveys = result.scalars().all()

    # Get total count
    count_result = await db.execute(select(Survey))
    total = len(count_result.scalars().all())

    return SurveyList(surveys=surveys, total=total)


@router.get("/{survey_id}", response_model=SurveySchema)
async def get_survey(survey_id: int, db: AsyncSession = Depends(get_db)):
    """Get survey by ID with questions and options."""
    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .options(selectinload(Survey.questions).selectinload(Question.options))
    )
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    return survey


@router.post("", response_model=SurveySchema, status_code=status.HTTP_201_CREATED)
async def create_survey(survey: SurveyCreate, db: AsyncSession = Depends(get_db)):
    """Create a new survey with questions."""
    # Extract questions from create data
    questions_data = survey.questions or []
    survey_dict = survey.model_dump(exclude={"questions"})

    db_survey = Survey(**survey_dict)
    db.add(db_survey)
    await db.flush()  # Get the survey ID

    # Add questions
    for question_data in questions_data:
        options_data = question_data.options or []
        question_dict = question_data.model_dump(exclude={"options"}, exclude_unset=True)

        db_question = Question(survey_id=db_survey.id, **question_dict)
        db.add(db_question)
        await db.flush()  # Get the question ID

        # Add options
        for option_data in options_data:
            db_option = QuestionOption(question_id=db_question.id, **option_data.model_dump())
            db.add(db_option)

    await db.commit()
    await db.refresh(db_survey)

    # Reload with relationships
    result = await db.execute(
        select(Survey)
        .where(Survey.id == db_survey.id)
        .options(selectinload(Survey.questions).selectinload(Question.options))
    )
    return result.scalar_one()


@router.put("/{survey_id}", response_model=SurveySchema)
async def update_survey(
    survey_id: int,
    survey_update: SurveyUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update survey."""
    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .options(selectinload(Survey.questions).selectinload(Question.options))
    )
    db_survey = result.scalar_one_or_none()

    if not db_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    update_data = survey_update.model_dump(exclude_unset=True, exclude={"questions"})
    for field, value in update_data.items():
        setattr(db_survey, field, value)

    # Handle questions update if provided
    if survey_update.questions is not None:
        # Delete existing questions and options
        for question in db_survey.questions:
            for option in question.options:
                await db.delete(option)
            await db.delete(question)

        # Add new questions
        for question_data in survey_update.questions:
            options_data = question_data.options or []
            question_dict = question_data.model_dump(exclude={"options"}, exclude_unset=True)

            db_question = Question(survey_id=db_survey.id, **question_dict)
            db.add(db_question)
            await db.flush()

            for option_data in options_data:
                db_option = QuestionOption(question_id=db_question.id, **option_data.model_dump())
                db.add(db_option)

    await db.commit()
    await db.refresh(db_survey)

    # Reload with relationships
    result = await db.execute(
        select(Survey)
        .where(Survey.id == survey_id)
        .options(selectinload(Survey.questions).selectinload(Question.options))
    )
    return result.scalar_one()


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_survey(survey_id: int, db: AsyncSession = Depends(get_db)):
    """Delete survey."""
    result = await db.execute(select(Survey).where(Survey.id == survey_id))
    db_survey = result.scalar_one_or_none()

    if not db_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    await db.delete(db_survey)
    await db.commit()

    return None
