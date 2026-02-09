"""
Сервис для отправки уведомлений через Telegram бот.
"""
import logging
from typing import Optional
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Employee, Survey, SurveyResponse
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для управления уведомлениями в Telegram."""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_survey_invite(
        self,
        employee_id: int,
        survey_id: int,
        db: AsyncSession
    ) -> dict:
        """
        Отправка приглашения на прохождение опроса сотруднику.

        Args:
            employee_id: ID сотрудника
            survey_id: ID опроса
            db: Сессия базы данных

        Returns:
            Словарь с результатом отправки
        """
        try:
            # Получаем данные из базы данных
            employee_result = await db.execute(
                select(Employee).where(Employee.id == employee_id)
            )
            employee = employee_result.scalar_one_or_none()

            if not employee:
                logger.error(f"Employee with id={employee_id} not found")
                return {"success": False, "error": "Employee not found"}

            survey_result = await db.execute(
                select(Survey).where(Survey.id == survey_id)
            )
            survey = survey_result.scalar_one_or_none()

            if not survey:
                logger.error(f"Survey with id={survey_id} not found")
                return {"success": False, "error": "Survey not found"}

            # Формируем сообщение
            message = (
                f"👋 <b>Привет, {employee.first_name}!</b>\n\n"
                f"Вас приглашают пройти опрос: <b>{survey.title}</b>\n\n"
                f"{survey.description if survey.description else 'Описание опроса отсутствует.'}\n\n"
                f"Для начала прохождения опроса нажмите кнопку ниже:"
            )

            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=employee.telegram_id,
                text=message,
                parse_mode="HTML"
            )

            logger.info(
                f"Survey invite sent to employee {employee.first_name} "
                f"({employee.telegram_id}) for survey '{survey.title}'"
            )

            return {
                "success": True,
                "employee_telegram_id": employee.telegram_id,
                "survey_title": survey.title,
                "message_id": None  # aiogram не возвращает message_id для отправки сообщений
            }

        except Exception as e:
            logger.error(f"Error sending survey invite: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def send_reminder(
        self,
        employee_id: int,
        survey_id: int,
        db: AsyncSession,
        days_remaining: Optional[int] = None
    ) -> dict:
        """
        Отправка напоминания о прохождении опроса.

        Args:
            employee_id: ID сотрудника
            survey_id: ID опроса
            db: Сессия базы данных
            days_remaining: Количество дней до дедлайна (опционально)

        Returns:
            Словарь с результатом отправки
        """
        try:
            # Получаем данные из базы данных
            employee_result = await db.execute(
                select(Employee).where(Employee.id == employee_id)
            )
            employee = employee_result.scalar_one_or_none()

            if not employee:
                logger.error(f"Employee with id={employee_id} not found")
                return {"success": False, "error": "Employee not found"}

            survey_result = await db.execute(
                select(Survey).where(Survey.id == survey_id)
            )
            survey = survey_result.scalar_one_or_none()

            if not survey:
                logger.error(f"Survey with id={survey_id} not found")
                return {"success": False, "error": "Survey not found"}

            # Формируем сообщение
            message_parts = [
                f"⏰ <b>Напоминание!</b>\n\n",
                f"У вас есть опрос: <b>{survey.title}</b>\n\n"
            ]

            if days_remaining is not None:
                message_parts.append(
                    f"⏳ До дедлайна осталось <b>{days_remaining} дн.</b>\n\n"
                )

            message_parts.extend([
                f"{survey.description if survey.description else 'Описание опроса отсутствует.'}\n\n",
                f"Для продолжения прохождения опроса нажмите кнопку ниже:"
            ])

            message = "".join(message_parts)

            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=employee.telegram_id,
                text=message,
                parse_mode="HTML"
            )

            logger.info(
                f"Reminder sent to employee {employee.first_name} "
                f"({employee.telegram_id}) for survey '{survey.title}'"
            )

            return {
                "success": True,
                "employee_telegram_id": employee.telegram_id,
                "survey_title": survey.title,
                "message_id": None
            }

        except Exception as e:
            logger.error(f"Error sending reminder: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def send_survey_completion_notification(
        self,
        hr_telegram_id: int,
        employee_name: str,
        survey_title: str
    ) -> dict:
        """
        Отправка уведомления HR о завершении опроса сотрудником.

        Args:
            hr_telegram_id: Telegram ID HR
            employee_name: Имя сотрудника
            survey_title: Название опроса

        Returns:
            Словарь с результатом отправки
        """
        try:
            message = (
                f"✅ <b>Опрос завершен!</b>\n\n"
                f"Сотрудник: <b>{employee_name}</b>\n"
                f"Опрос: <b>{survey_title}</b>\n\n"
                f"Результаты доступны в админ-панели."
            )

            await self.bot.send_message(
                chat_id=hr_telegram_id,
                text=message,
                parse_mode="HTML"
            )

            logger.info(
                f"Survey completion notification sent to HR "
                f"({hr_telegram_id}) for employee '{employee_name}'"
            )

            return {
                "success": True,
                "hr_telegram_id": hr_telegram_id,
                "message_id": None
            }

        except Exception as e:
            logger.error(
                f"Error sending survey completion notification: {str(e)}",
                exc_info=True
            )
            return {
                "success": False,
                "error": str(e)
            }

    async def send_multiple_reminders(
        self,
        survey_id: int,
        db: AsyncSession,
        days: list[int] = [3, 1, 0]  # Напоминания за 3, 1 день и в день дедлайна
    ) -> dict:
        """
        Отправка серии напоминаний для всех сотрудников, у которых есть опрос.

        Args:
            survey_id: ID опроса
            db: Сессия базы данных
            days: Список дней до дедлайна для отправки напоминаний

        Returns:
            Словарь с результатами отправки
        """
        try:
            # Получаем опрос
            survey_result = await db.execute(
                select(Survey).where(Survey.id == survey_id)
            )
            survey = survey_result.scalar_one_or_none()

            if not survey:
                logger.error(f"Survey with id={survey_id} not found")
                return {"success": False, "error": "Survey not found"}

            # Получаем все ответы с pending статусом
            responses_result = await db.execute(
                select(SurveyResponse).where(
                    SurveyResponse.survey_id == survey_id,
                    SurveyResponse.status == "pending"
                )
            )
            responses = responses_result.scalars().all()

            results = []
            for response in responses:
                employee_result = await db.execute(
                    select(Employee).where(Employee.id == response.employee_id)
                )
                employee = employee_result.scalar_one_or_none()

                if not employee:
                    logger.warning(f"Employee not found for response {response.id}")
                    continue

                # Отправляем напоминание для каждого дня
                for day in days:
                    result = await self.send_reminder(
                        employee_id=employee.id,
                        survey_id=survey_id,
                        db=db,
                        days_remaining=day
                    )
                    results.append({
                        "employee_id": employee.id,
                        "employee_name": f"{employee.first_name} {employee.last_name}",
                        "telegram_id": employee.telegram_id,
                        "day": day,
                        **result
                    })

            logger.info(
                f"Sent {len(results)} reminder notifications for survey '{survey.title}'"
            )

            return {
                "success": True,
                "total_sent": len(results),
                "results": results
            }

        except Exception as e:
            logger.error(f"Error sending multiple reminders: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
