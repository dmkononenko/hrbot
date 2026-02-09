# API Документация

Полная документация API HR Bot.

## Базовый URL

```
http://localhost:8000/api/v1
```

## Общая информация

### Методы HTTP

- `GET` — Получение данных
- `POST` — Создание ресурса
- `PUT` — Полное обновление ресурса
- `PATCH` — Частичное обновление ресурса
- `DELETE` — Удаление ресурса

### Формат ответа

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Коды статусов

- `200 OK` — Успешный запрос
- `201 Created` — Ресурс создан
- `204 No Content` — Успешное удаление
- `400 Bad Request` — Неверный запрос
- `404 Not Found` — Ресурс не найден
- `500 Internal Server Error` — Ошибка сервера

---

## Опросы (Surveys)

### Получить список опросов

**Endpoint**: `GET /surveys`

**Параметры запроса**:
- `skip` (integer, optional) — Пропустить записей (по умолчанию: 0)
- `limit` (integer, optional) — Количество записей (по умолчанию: 100)
- `active_only` (boolean, optional) — Только активные опросы (по умолчанию: false)

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/surveys?skip=0&limit=10&active_only=false"
```

**Пример ответа**:
```json
{
  "surveys": [
    {
      "id": 1,
      "title": "90-Day Check-in",
      "description": "Как вам работаеться?",
      "days_after_start": 90,
      "is_active": true,
      "created_at": "2025-11-10T00:00:00Z",
      "updated_at": "2025-11-10T00:00:00Z",
      "questions": [
        {
          "id": 1,
          "survey_id": 1,
          "question_text": "Насколько вы удовлетворены?",
          "question_type": "single_choice",
          "order_index": 0,
          "is_required": true,
          "options": [
            {
              "id": 1,
              "question_id": 1,
              "option_text": "Очень доволен",
              "order_index": 0
            }
          ]
        }
      ]
    }
  ],
  "total": 1
}
```

### Получить опрос по ID

**Endpoint**: `GET /surveys/{survey_id}`

**Параметры**:
- `survey_id` (integer, path) — ID опроса

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/surveys/1"
```

**Пример ответа**:
```json
{
  "id": 1,
  "title": "90-Day Check-in",
  "description": "Как вам работаеться?",
  "days_after_start": 90,
  "is_active": true,
  "created_at": "2025-11-10T00:00:00Z",
  "updated_at": "2025-11-10T00:00:00Z",
  "questions": [...]
}
```

### Создать опрос

**Endpoint**: `POST /surveys`

**Тело запроса**:
```json
{
  "title": "90-Day Check-in",
  "description": "Как вам работаеться?",
  "days_after_start": 90,
  "is_active": true,
  "questions": [
    {
      "question_text": "Насколько вы удовлетворены?",
      "question_type": "single_choice",
      "order_index": 0,
      "is_required": true,
      "options": [
        {
          "option_text": "Очень доволен",
          "order_index": 0
        },
        {
          "option_text": "Доволен",
          "order_index": 1
        }
      ]
    }
  ]
}
```

**Типы вопросов**:
- `text` — свободный ввод текста
- `single_choice` — выбор одного варианта
- `multiple_choice` — выбор нескольких вариантов

**Пример запроса**:
```bash
curl -X POST "http://localhost:8000/api/v1/surveys" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "90-Day Check-in",
    "description": "Как вам работаеться?",
    "days_after_start": 90,
    "is_active": true,
    "questions": [
      {
        "question_text": "Насколько вы удовлетворены?",
        "question_type": "single_choice",
        "order_index": 0,
        "is_required": true,
        "options": [
          {"option_text": "Очень доволен", "order_index": 0},
          {"option_text": "Доволен", "order_index": 1},
          {"option_text": "Нейтрально", "order_index": 2},
          {"option_text": "Недоволен", "order_index": 3}
        ]
      },
      {
        "question_text": "Что бы вы хотели улучшить?",
        "question_type": "multiple_choice",
        "order_index": 1,
        "is_required": true,
        "options": [
          {"option_text": "Коммуникация", "order_index": 0},
          {"option_text": "Обучение", "order_index": 1},
          {"option_text": "Инструменты", "order_index": 2},
          {"option_text": "Организация", "order_index": 3}
        ]
      },
      {
        "question_text": "Дополнительные комментарии",
        "question_type": "text",
        "order_index": 2,
        "is_required": false
      }
    ]
  }'
```

**Пример ответа**:
```json
{
  "id": 1,
  "title": "90-Day Check-in",
  "description": "Как вам работаеться?",
  "days_after_start": 90,
  "is_active": true,
  "created_at": "2025-11-10T00:00:00Z",
  "updated_at": "2025-11-10T00:00:00Z",
  "questions": [...]
}
```

### Обновить опрос

**Endpoint**: `PUT /surveys/{survey_id}`

**Тело запроса**:
```json
{
  "title": "90-Day Check-in (Updated)",
  "description": "Обновленное описание",
  "is_active": false
}
```

**Пример запроса**:
```bash
curl -X PUT "http://localhost:8000/api/v1/surveys/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "90-Day Check-in (Updated)",
    "description": "Обновленное описание",
    "is_active": false
  }'
```

### Удалить опрос

**Endpoint**: `DELETE /surveys/{survey_id}`

**Пример запроса**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/surveys/1"
```

**Пример ответа**: `204 No Content`

---

## Сотрудники (Employees)

### Получить список сотрудников

**Endpoint**: `GET /employees`

**Параметры запроса**:
- `skip` (integer, optional) — Пропустить записей (по умолчанию: 0)
- `limit` (integer, optional) — Количество записей (по умолчанию: 100)

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/employees?skip=0&limit=10"
```

**Пример ответа**:
```json
{
  "employees": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "telegram_username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "start_date": "2025-11-10",
      "is_active": true,
      "created_at": "2025-11-10T00:00:00Z",
      "updated_at": "2025-11-10T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Получить сотрудника по ID

**Endpoint**: `GET /employees/{employee_id}`

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/employees/1"
```

**Пример ответа**:
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "telegram_username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "start_date": "2025-11-10",
  "is_active": true,
  "created_at": "2025-11-10T00:00:00Z",
  "updated_at": "2025-11-10T00:00:00Z"
}
```

### Создать сотрудника

**Endpoint**: `POST /employees`

**Тело запроса**:
```json
{
  "telegram_id": 123456789,
  "telegram_username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "start_date": "2025-11-10",
  "is_active": true
}
```

**Пример запроса**:
```bash
curl -X POST "http://localhost:8000/api/v1/employees" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "telegram_username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "start_date": "2025-11-10",
    "is_active": true
  }'
```

**Пример ответа**:
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "telegram_username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "start_date": "2025-11-10",
  "is_active": true,
  "created_at": "2025-11-10T00:00:00Z",
  "updated_at": "2025-11-10T00:00:00Z"
}
```

### Обновить сотрудника

**Endpoint**: `PUT /employees/{employee_id}`

**Тело запроса**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "start_date": "2025-11-10",
  "is_active": true
}
```

**Пример запроса**:
```bash
curl -X PUT "http://localhost:8000/api/v1/employees/1" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "start_date": "2025-11-10",
    "is_active": true
  }'
```

### Удалить сотрудника

**Endpoint**: `DELETE /employees/{employee_id}`

**Пример запроса**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/employees/1"
```

**Пример ответа**: `204 No Content`

### Найти сотрудника по Telegram ID

**Endpoint**: `GET /employees/telegram/{telegram_id}`

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/employees/telegram/123456789"
```

**Пример ответа**:
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "telegram_username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "start_date": "2025-11-10",
  "is_active": true,
  "created_at": "2025-11-10T00:00:00Z",
  "updated_at": "2025-11-10T00:00:00Z"
}
```

---

## Ответы (Responses)

### Получить список всех ответов

**Endpoint**: `GET /responses`

**Параметры запроса**:
- `skip` (integer, optional) — Пропустить записей (по умолчанию: 0)
- `limit` (integer, optional) — Количество записей (по умолчанию: 100)
- `survey_id` (integer, optional) — Фильтр по опросу

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/responses?skip=0&limit=10&survey_id=1"
```

**Пример ответа**:
```json
{
  "responses": [
    {
      "id": 1,
      "survey_id": 1,
      "employee_id": 1,
      "status": "completed",
      "completed_at": "2025-11-10T12:00:00Z",
      "answers": [
        {
          "id": 1,
          "survey_response_id": 1,
          "question_id": 1,
          "answer_text": "Очень доволен",
          "answer_options": [1]
        }
      ],
      "employee": {
        "id": 1,
        "telegram_id": 123456789,
        "telegram_username": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
      }
    }
  ],
  "total": 1
}
```

### Получить ответ по ID

**Endpoint**: `GET /responses/{response_id}`

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/responses/1"
```

**Пример ответа**:
```json
{
  "id": 1,
  "survey_id": 1,
  "employee_id": 1,
  "status": "completed",
  "completed_at": "2025-11-10T12:00:00Z",
  "answers": [...],
  "employee": {...}
}
```

### Получить результаты опроса (JSON формат)

**Endpoint**: `GET /surveys/{survey_id}/results`

**Параметры**:
- `survey_id` (integer, path) — ID опроса

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/surveys/1/results"
```

**Пример ответа**:
```json
{
  "survey_id": 1,
  "survey_title": "90-Day Check-in",
  "responses": [
    {
      "response_id": 1,
      "employee": {
        "id": 1,
        "telegram_id": 123456789,
        "telegram_username": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "completed_at": "2025-11-10T12:00:00Z",
      "answers": [
        {
          "question_id": 1,
          "question_text": "Насколько вы удовлетворены?",
          "question_type": "single_choice",
          "answer_text": "Очень доволен",
          "answer_options": ["Очень доволен"]
        },
        {
          "question_id": 2,
          "question_text": "Что бы вы хотели улучшить?",
          "question_type": "multiple_choice",
          "answer_text": null,
          "answer_options": ["Коммуникация", "Инструменты"]
        },
        {
          "question_id": 3,
          "question_text": "Дополнительные комментарии",
          "question_type": "text",
          "answer_text": "Всё отлично!",
          "answer_options": null
        }
      ]
    }
  ],
  "total_responses": 1,
  "completion_rate": 1.0
}
```

---

## Telegram Bot API

### Webhook endpoint

**Endpoint**: `POST /bot/webhook`

**Описание**: Telegram webhook endpoint для получения обновлений от Telegram.

**Пример запроса**:
```bash
curl -X POST "http://localhost:8000/api/v1/bot/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123,
    "message": {
      "message_id": 1,
      "from": {
        "id": 123456789,
        "is_bot": false,
        "first_name": "John",
        "username": "johndoe"
      },
      "chat": {
        "id": 123456789,
        "type": "private"
      },
      "date": 1699999999,
      "text": "/start"
    }
  }'
```

**Пример ответа**:
```json
{
  "status": "ok"
}
```

### Инициировать опрос для сотрудника

**Endpoint**: `POST /bot/initiate-survey`

**Описание**: HR инициирует опрос для сотрудника. Проверяет, что сотрудник прошел 90+ дней работы.

**Тело запроса**:
```json
{
  "employee_telegram_id": 123456789,
  "survey_id": 1
}
```

**Пример запроса**:
```bash
curl -X POST "http://localhost:8000/api/v1/bot/initiate-survey" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_telegram_id": 123456789,
    "survey_id": 1
  }'
```

**Пример ответа**:
```json
{
  "message": "Survey initiated successfully",
  "response_id": 1,
  "employee_telegram_id": 123456789,
  "survey_id": 1,
  "invite_sent": true,
  "invite_error": null
}
```

### Получить список доступных опросов для пользователя

**Endpoint**: `GET /bot/surveys/{telegram_id}`

**Описание**: Получение списка опросов, к которым сотрудник еще не отвечал.

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/bot/surveys/123456789"
```

**Пример ответа**:
```json
{
  "telegram_id": 123456789,
  "surveys": [
    {
      "id": 1,
      "title": "90-Day Check-in",
      "description": "Как вам работаеться?",
      "is_active": true,
      "days_after_start": 90,
      "questions_count": 3
    }
  ],
  "total": 1
}
```

### Получить список подходящих сотрудников

**Endpoint**: `GET /bot/eligible-employees/{survey_id}`

**Описание**: Получение списка сотрудников, прошедших указанное количество дней работы.

**Пример запроса**:
```bash
curl "http://localhost:8000/api/v1/bot/eligible-employees/1"
```

**Пример ответа**:
```json
{
  "survey_id": 1,
  "days_after_start": 90,
  "eligible_employees": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "first_name": "John",
      "last_name": "Doe",
      "start_date": "2025-11-10",
      "days_since_start": 90
    },
    {
      "id": 2,
      "telegram_id": 987654321,
      "first_name": "Jane",
      "last_name": "Smith",
      "start_date": "2025-08-15",
      "days_since_start": 120
    }
  ],
  "total": 2
}
```

### Отправить приглашение на опрос

**Endpoint**: `POST /bot/send-invite`

**Описание**: Отправка приглашения на прохождение опроса сотруднику.

**Тело запроса**:
```json
{
  "employee_id": 1,
  "survey_id": 1
}
```

**Пример запроса**:
```bash
curl -X POST "http://localhost:8000/api/v1/bot/send-invite" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "survey_id": 1
  }'
```

**Пример ответа**:
```json
{
  "success": true,
  "message": "Survey invitation sent to John Doe",
  "response_id": 1
}
```

### Отправить напоминание о опросе

**Endpoint**: `POST /bot/send-reminder`

**Описание**: Отправка напоминания о незавершенном опросе.

**Тело запроса**:
```json
{
  "employee_id": 1,
  "survey_id": 1,
  "days_remaining": 3
}
```

**Пример запроса**:
```bash
curl -X POST "http://localhost:8000/api/v1/bot/send-reminder" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "survey_id": 1,
    "days_remaining": 3
  }'
```

**Пример ответа**:
```json
{
  "success": true,
  "message": "Reminder sent to John Doe"
}
```

### Отправить batch напоминаний

**Endpoint**: `POST /bot/send-reminders-batch`

**Описание**: Отправка серии напоминаний всем сотрудникам, у которых есть опрос.

**Тело запроса**:
```json
{
  "survey_id": 1,
  "days": [3, 1, 0]
}
```

**Пример запроса**:
```bash
curl -X POST "http://localhost:8000/api/v1/bot/send-reminders-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "survey_id": 1,
    "days": [3, 1, 0]
  }'
```

**Пример ответа**:
```json
{
  "success": true,
  "message": "Batch reminders sent",
  "total_sent": 5
}
```

---

## Примеры использования

### Полный цикл работы с опросом

```bash
# 1. Создать опрос
curl -X POST "http://localhost:8000/api/v1/surveys" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "90-Day Check-in",
    "description": "Как вам работаеться?",
    "days_after_start": 90,
    "is_active": true,
    "questions": [
      {
        "question_text": "Насколько вы удовлетворены?",
        "question_type": "single_choice",
        "order_index": 0,
        "is_required": true,
        "options": [
          {"option_text": "Очень доволен", "order_index": 0},
          {"option_text": "Доволен", "order_index": 1},
          {"option_text": "Нейтрально", "order_index": 2},
          {"option_text": "Недоволен", "order_index": 3}
        ]
      }
    ]
  }'

# Ответ: {"id": 1, ...}

# 2. Зарегистрировать сотрудника
curl -X POST "http://localhost:8000/api/v1/employees" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 123456789,
    "telegram_username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "start_date": "2025-11-10"
  }'

# Ответ: {"id": 1, ...}

# 3. Инициировать опрос для сотрудника
curl -X POST "http://localhost:8000/api/v1/bot/initiate-survey" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_telegram_id": 123456789,
    "survey_id": 1
  }'

# Ответ: {"message": "Survey initiated successfully", "response_id": 1, ...}

# 4. Получить результаты опроса
curl "http://localhost:8000/api/v1/surveys/1/results"

# Ответ: {"survey_id": 1, "survey_title": "90-Day Check-in", "responses": [...], ...}
```

---

## Типы данных

### Survey (Опрос)

```typescript
interface Survey {
  id: number;
  title: string;
  description: string;
  days_after_start: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  questions: Question[];
}
```

### Question (Вопрос)

```typescript
interface Question {
  id: number;
  survey_id: number;
  question_text: string;
  question_type: 'text' | 'single_choice' | 'multiple_choice';
  order_index: number;
  is_required: boolean;
  options?: QuestionOption[];
}
```

### QuestionOption (Вариант ответа)

```typescript
interface QuestionOption {
  id: number;
  question_id: number;
  option_text: string;
  order_index: number;
}
```

### Employee (Сотрудник)

```typescript
interface Employee {
  id: number;
  telegram_id: number;
  telegram_username: string;
  first_name: string;
  last_name: string;
  start_date: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
```

### SurveyResponse (Ответ на опрос)

```typescript
interface SurveyResponse {
  id: number;
  survey_id: number;
  employee_id: number;
  status: 'pending' | 'completed';
  completed_at: string | null;
  answers: Answer[];
  employee: Employee;
}
```

### Answer (Детализация ответа)

```typescript
interface Answer {
  id: number;
  survey_response_id: number;
  question_id: number;
  answer_text: string | null;
  answer_options: number[] | null;
}
```

---

## Ограничения

- `limit` параметр ограничивает количество возвращаемых записей (максимум 100)
- `skip` параметр позволяет пагинаровать результаты
- Опросы с `is_active: false` не показываются сотрудникам
- Сотрудник может отвечать на опрос только один раз
