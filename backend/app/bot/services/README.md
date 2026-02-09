# Сервис уведомлений

Этот модуль предоставляет функционал для отправки уведомлений через Telegram бот.

## Функциональность

### Основные функции

1. **send_survey_invite(employee_id, survey_id, db)** - Отправка приглашения на прохождение опроса сотруднику
2. **send_reminder(employee_id, survey_id, db, days_remaining)** - Отправка напоминания о прохождении опроса
3. **send_survey_completion_notification(hr_telegram_id, employee_name, survey_title)** - Уведомление HR о завершении опроса
4. **send_multiple_reminders(survey_id, db, days)** - Отправка серии напоминаний всем сотрудникам

## Использование

### Инициализация

```python
from app.bot.bot import bot
from app.bot.services.notification_service import NotificationService

notification_service = NotificationService(bot)
```

### Отправка приглашения на опрос

```python
result = await notification_service.send_survey_invite(
    employee_id=1,
    survey_id=1,
    db=db
)

if result["success"]:
    print(f"Приглашение отправлено: {result['employee_telegram_id']}")
else:
    print(f"Ошибка: {result['error']}")
```

### Отправка напоминания

```python
result = await notification_service.send_reminder(
    employee_id=1,
    survey_id=1,
    db=db,
    days_remaining=3  # Количество дней до дедлайна
)
```

### Отправка серии напоминаний

```python
result = await notification_service.send_multiple_reminders(
    survey_id=1,
    db=db,
    days=[3, 1, 0]  # Напоминания за 3, 1 день и в день дедлайна
)

print(f"Отправлено уведомлений: {result['total_sent']}")
for res in result['results']:
    print(f"Сотрудник: {res['employee_name']}, "
          f"Telegram ID: {res['telegram_id']}, "
          f"День: {res['day']}")
```

### Уведомление HR о завершении опроса

```python
result = await notification_service.send_survey_completion_notification(
    hr_telegram_id=123456789,
    employee_name="Иван Иванов",
    survey_title="Ежегодная оценка"
)
```

## Обработка ошибок

Все функции возвращают словарь с результатом:

```python
{
    "success": True/False,
    "employee_telegram_id": 123456789,  # Только для приглашений и напоминаний
    "survey_title": "Название опроса",  # Только для приглашений и напоминаний
    "message_id": None,  # aiogram не возвращает message_id для отправки сообщений
    "error": "Ошибка"  # Только если success=False
}
```

## Примеры ошибок

1. **Сотрудник не найден**
   ```python
   result = await notification_service.send_survey_invite(999, 1, db)
   # {"success": False, "error": "Employee not found"}
   ```

2. **Опрос не найден**
   ```python
   result = await notification_service.send_survey_invite(1, 999, db)
   # {"success": False, "error": "Survey not found"}
   ```

3. **Бот заблокирован или не запущен**
   ```python
   result = await notification_service.send_survey_invite(1, 1, db)
   # {"success": False, "error": "Bot was blocked by the user"}
   ```

## Логирование

Все операции логируются с уровнем INFO или ERROR:

- Успешная отправка: `logger.info(...)`
- Ошибка при отправке: `logger.error(..., exc_info=True)`

## API Эндпоинты

См. [`backend/app/api/v1/bot.py`](../api/v1/bot.py) для списка доступных API эндпоинтов.
