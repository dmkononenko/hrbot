#!/usr/bin/env python3
"""
Initialize the standard onboarding survey.
Creates the survey with questions if it doesn't exist.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory so DATABASE_URL works correctly
os.chdir(backend_dir)

from app.database import async_session
from app.models import Survey, Question, QuestionOption
from sqlalchemy import select


async def init_onboarding_survey():
    """Initialize the standard onboarding survey."""
    async with async_session() as db:
        # Check if survey already exists
        result = await db.execute(
            select(Survey).where(Survey.title == "Онбординг опросник")
        )
        existing_survey = result.scalar_one_or_none()

        if existing_survey:
            print("✓ Onboarding survey already exists. Skipping creation.")
            return

        # Create the survey
        survey = Survey(
            title="Онбординг опросник",
            description="Опрос для оценки адаптации новых сотрудников по итогам испытательного срока.",
            days_after_start=90,
            is_active=True
        )
        db.add(survey)
        await db.flush()  # Get the survey ID

        # Questions data
        questions_data = [
            {
                "order": 1,
                "text_ru": "Насколько вам понятны ваши задачи и ожидания от вас по итогам испытательного срока?",
                "text_kg": "Сыноо мөөнтүнүн жыйынтыгы боюнча Сиздин тапшырмалар жана Сизден болгон күтүүлөр Сизге канчалык түшүнүктүү?",
                "type": "single_choice",
            },
            {
                "order": 2,
                "text_ru": "Насколько у вас было всё необходимое для выполнения работы: доступы?",
                "text_kg": "Ишти аткаруу үчүн бардык зарыл нерселер Сизде канчалык болду жетүүлөр?",
                "type": "single_choice",
            },
            {
                "order": 3,
                "text_ru": "Насколько у вас было всё необходимое для выполнения работы: оборудование?",
                "text_kg": "Ишти аткаруу үчүн бардык зарыл нерселер Сизде канчалык болду инструменттер?",
                "type": "single_choice",
            },
            {
                "order": 4,
                "text_ru": "Насколько вам хватало поддержки и обратной связи от руководителя в период испытательного срока?",
                "text_kg": "Сыноо мөөнөтүнүн ичинде жетекчиңиздин колдоосу жана кайтарым байланышы Сизге канчалык жетиштүү болду?",
                "type": "single_choice",
            },
            {
                "order": 5,
                "text_ru": "Насколько комфортно вам было взаимодействовать с командой?",
                "text_kg": "Сизге команда менен өз ара аракеттешүү канчалык ыңгайлуу болду?",
                "type": "single_choice",
            },
            {
                "order": 6,
                "text_ru": "Как вы в целом оцениваете свою адаптацию в компании по итогам испытательного срока?",
                "text_kg": "Сыноо мөөнөтүнүн жыйынтыктары боюнча Сиздин компанияга көнүүңүздү жалпысынан кандай баалайсыз?",
                "type": "single_choice",
            },
            {
                "order": 7,
                "text_ru": "Насколько вероятно, что вы порекомендуете ОАО «О!Банк» как место работы своим знакомым?",
                "text_kg": "Сиздин «О!Банк» ААКты жумуш орду катары тааныштарыңызга сунуштооңуз канчалык ыктымалдуу?",
                "type": "single_choice",
            },
            {
                "order": 8,
                "text_ru": "Что, на ваш взгляд, можно улучшить в процессе адаптации новых сотрудников?",
                "text_kg": "Сиздин көз карашыңыз боюнча жаңы кызматкерлердин көнүү процессинде эмнени жакшыртса болот?",
                "type": "text",
            },
        ]

        # Rating options (1-5)
        rating_options = [
            {"order": 1, "text": "1"},
            {"order": 2, "text": "2"},
            {"order": 3, "text": "3"},
            {"order": 4, "text": "4"},
            {"order": 5, "text": "5"},
        ]

        # Create questions
        for q_data in questions_data:
            question = Question(
                survey_id=survey.id,
                question_text=q_data["text_ru"],  # Using RU as default
                question_text_ru=q_data["text_ru"],
                question_text_kg=q_data["text_kg"],
                question_type=q_data["type"],
                order_index=q_data["order"],
                is_required=True
            )
            db.add(question)
            await db.flush()  # Get the question ID

            # Add options for single_choice questions
            if q_data["type"] == "single_choice":
                for opt_data in rating_options:
                    option = QuestionOption(
                        question_id=question.id,
                        option_text=opt_data["text"],
                        order_index=opt_data["order"]
                    )
                    db.add(option)

        await db.commit()
        print("✓ Onboarding survey created successfully!")
        print(f"  Survey ID: {survey.id}")
        print(f"  Questions: {len(questions_data)}")


async def main():
    """Initialize the onboarding survey."""
    print("Initializing onboarding survey...")
    await init_onboarding_survey()
    print("\nNext steps:")
    print("  1. Start the bot: python -m app.bot.main")
    print("  2. The survey will be available to all employees")


if __name__ == "__main__":
    asyncio.run(main())
