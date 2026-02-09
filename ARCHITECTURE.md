# Архитектура HR Bot

## Общая архитектура

HR Bot представляет собой микросервисную архитектуру с разделением на три основных компонента:

1. **Backend** — FastAPI сервер с API и логикой бота
2. **Telegram Bot** — Aiogram бот для взаимодействия с пользователями
3. **Frontend** — React приложение для админ-панели

```
┌─────────────────────────────────────────────────────────────┐
│                        HR Bot Architecture                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐
│   Telegram Bot   │         │   Frontend App  │
│   (Aiogram)      │◄───────►│   (React)       │
└────────┬────────┘         └────────┬────────┘
         │                          │
         │                          │
         │                          │
         ▼                          ▼
┌──────────────────────────────────────────────────────┐
│                   Backend API                         │
│  ┌──────────────────────────────────────────────┐   │
│  │           API Endpoints (FastAPI)             │   │
│  │  - /api/v1/surveys    (CRUD опросов)         │   │
│  │  - /api/v1/employees  (CRUD сотрудников)     │   │
│  │  - /api/v1/responses  (CRUD ответов)         │   │
│  │  - /api/v1/bot        (Bot API)              │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │         Business Logic & Services            │   │
│  │  - Survey Service                           │   │
│  │  - Employee Service                         │   │
│  │  - Notification Service                     │   │
│  │  - Eligibility Checker                      │   │
│  └──────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────┐   │
│  │           Bot Handlers & FSM                 │   │
│  │  - Message Handlers                          │   │
│  │  - State Machine (FSM)                       │   │
│  │  - Keyboard Factories                        │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
         │
         │
         ▼
┌──────────────────────────────────────────────────────┐
│                  Database Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Employees │  │    Surveys  │  │  Responses  │  │
│  │   Table     │  │    Table    │  │    Table    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│  ┌─────────────┐  ┌─────────────┐                    │
│  │  Questions  │  │  Question   │                    │
│  │    Table    │  │   Options   │                    │
│  └─────────────┘  └─────────────┘                    │
│  ┌─────────────────────────────────────────────┐     │
│  │          SQLAlchemy ORM + SQLite            │     │
│  └─────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────┘
```

## Структура проекта

### Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py                    # Точка входа приложения
│   ├── config.py                  # Конфигурация (Pydantic Settings)
│   ├── database.py                # Подключение к БД
│   ├── models/                    # SQLAlchemy модели
│   │   ├── employee.py            # Модель сотрудника
│   │   ├── survey.py              # Модель опроса
│   │   ├── response.py            # Модель ответа
│   │   └── __init__.py
│   ├── schemas/                   # Pydantic схемы
│   │   ├── employee.py            # Схемы для сотрудников
│   │   ├── survey.py              # Схемы для опросов
│   │   ├── response.py            # Схемы для ответов
│   │   └── __init__.py
│   ├── api/v1/                    # API версии 1
│   │   ├── __init__.py
│   │   ├── surveys.py             # Опросы (CRUD)
│   │   ├── employees.py           # Сотрудники (CRUD)
│   │   ├── responses.py           # Ответы (CRUD + результаты)
│   │   └── bot.py                 # Bot API
│   ├── bot/                       # Aiogram бот
│   │   ├── __init__.py
│   │   ├── bot.py                 # Основной бот
│   │   ├── handlers/              # Обработчики сообщений
│   │   │   ├── __init__.py
│   │   │   ├── start.py           # Стартовый обработчик
│   │   │   └── survey.py          # Обработчики опросов
│   │   ├── keyboards/             # Клавиатуры бота
│   │   │   ├── __init__.py
│   │   │   └── keyboards.py       # Фабрики клавиатур
│   │   ├── services/              # Бизнес-логика бота
│   │   │   ├── __init__.py
│   │   │   ├── notification_service.py  # Сервис уведомлений
│   │   │   └── README.md
│   │   └── fsm/                   # Машина состояний
│   │       ├── __init__.py
│   │       └── states.py          # Определение состояний
│   ├── core/                      # Ядро приложения
│   │   └── __init__.py
│   └── utils/                     # Утилиты
│       └── __init__.py
├── requirements.txt               # Python зависимости
├── .env.example                   # Пример конфигурации
└── hrbot.db                       # База данных (SQLite)
```

### Frontend (React)

```
frontend/
├── src/
│   ├── components/                # React компоненты
│   │   ├── surveys/               # Компоненты для опросов
│   │   │   ├── index.ts
│   │   │   ├── QuestionAdder.tsx  # Добавление вопросов
│   │   │   └── QuestionEditor.tsx # Редактирование вопросов
│   │   ├── employees/             # Компоненты для сотрудников
│   │   │   └── EmployeeForm.tsx   # Форма сотрудника
│   │   ├── results/               # Компоненты для результатов
│   │   │   └── AnswerViewer.tsx   # Просмотр ответов
│   │   └── ui/                    # UI компоненты
│   │       ├── index.ts
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Select.tsx
│   │       ├── Modal.tsx
│   │       ├── Card.tsx
│   │       ├── Table.tsx
│   │       ├── Badge.tsx
│   │       └── Status.tsx
│   ├── pages/                     # Страницы приложения
│   │   ├── Dashboard.tsx          # Панель управления
│   │   ├── Surveys.tsx            # Список опросов
│   │   ├── Employees.tsx          # Список сотрудников
│   │   ├── Results.tsx            # Все ответы
│   │   └── SurveyResults.tsx      # Результаты конкретного опроса
│   ├── services/                  # API клиент
│   │   └── api.ts                 # Axios инстанс
│   ├── types/                     # TypeScript типы
│   │   └── index.ts               # Общие типы
│   ├── App.tsx                    # Главный компонент
│   ├── main.tsx                   # Точка входа
│   └── index.css                  # Глобальные стили
├── package.json                   # Node зависимости
├── tsconfig.json                  # TypeScript конфигурация
├── vite.config.ts                 # Vite конфигурация
└── .env                           # Переменные окружения
```

### Scripts

```
scripts/
├── init_db.py                     # Инициализация БД
└── start_dev.sh                   # Запуск разработки
```

## Компоненты системы

### 1. Backend API (FastAPI)

**Назначение**: Предоставляет REST API для управления данными.

**Ключевые компоненты**:

- **API Endpoints**:
  - `surveys.py` — CRUD операции для опросов
  - `employees.py` — CRUD операции для сотрудников
  - `responses.py` — CRUD операции для ответов и результаты
  - `bot.py` — API для взаимодействия с ботом

- **Модели данных** (SQLAlchemy):
  - `Employee` — сотрудник с контактами и датой начала работы
  - `Survey` — опрос с настройками и связанными вопросами
  - `Question` — вопрос с типом и вариантами ответов
  - `QuestionOption` — вариант ответа
  - `SurveyResponse` — ответ сотрудника на опрос
  - `Answer` — детализация ответа

- **Схемы данных** (Pydantic):
  - Валидация входных данных
  - Сериализация/десериализация
  - Автодокументация (Swagger/OpenAPI)

### 2. Telegram Bot (Aiogram 3.x)

**Назначение**: Обеспечивает взаимодействие с пользователями через Telegram.

**Архитектура бота**:

```
Bot
├── Dispatcher (диспетчер сообщений)
├── Handlers (обработчики)
│   ├── start.py (обработчик /start)
│   └── survey.py (обработчики опросов)
├── FSM (Машина состояний)
│   ├── states.py (определение состояний)
│   └── переходы между состояниями
├── Keyboards (клавиатуры)
│   └── keyboards.py (фабрики клавиатур)
└── Services (сервисы)
    └── notification_service.py (уведомления)
```

**Workflow опроса**:

```
1. HR инициирует опрос для сотрудника
   ↓
2. Сотрудник получает приглашение в Telegram
   ↓
3. Сотрудник нажимает "Начать опрос"
   ↓
4. FSM переходит в состояние SURVEY_START
   ↓
5. Показывается первый вопрос
   ↓
6. Сотрудник отвечает
   ↓
7. FSM переходит к следующему вопросу
   ↓
8. Повторяется до последнего вопроса
   ↓
9. Опрос завершен, FSM переходит в SURVEY_COMPLETED
   ↓
10. Сотрудник получает подтверждение
```

### 3. Frontend (React + TypeScript)

**Назначение**: Админ-панель для управления опросами и сотрудниками.

**Стек технологий**:
- React 18 с хуками
- TypeScript для типобезопасности
- Vite для быстрой сборки
- React Router для навигации
- TanStack React Query для кэширования
- Axios для HTTP запросов
- Zod + React Hook Form для валидации

**Структура страниц**:

1. **Dashboard** — общая статистика
2. **Surveys** — управление опросами
3. **Employees** — управление сотрудниками
4. **Results** — все ответы
5. **SurveyResults** — детальные результаты опроса

## Взаимодействие компонентов

### API <-> Database

```
Frontend → API (FastAPI) → SQLAlchemy ORM → SQLite
```

- Frontend отправляет HTTP запросы к API
- API использует SQLAlchemy для работы с БД
- БД хранит все данные в структурированном виде

### API <-> Telegram Bot

```
HR (Admin) → API → Bot Service → Telegram Bot
```

- HR использует API для инициирования опросов
- API вызывает сервис бота
- Бот отправляет сообщение сотруднику

### Frontend ↔ API

```
Frontend (React) → Axios → API (FastAPI)
```

- React компоненты делают запросы к API
- API возвращает JSON данные
- React Query кэширует данные

## Данные и модели

### Employee (Сотрудник)

```python
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

### Survey (Опрос)

```python
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

### Question (Вопрос)

```python
{
    "id": 1,
    "survey_id": 1,
    "question_text": "Насколько вы удовлетворены?",
    "question_type": "single_choice",
    "order_index": 0,
    "is_required": true,
    "options": [...]
}
```

### SurveyResponse (Ответ на опрос)

```python
{
    "id": 1,
    "survey_id": 1,
    "employee_id": 1,
    "status": "completed",
    "completed_at": "2025-11-10T12:00:00Z",
    "answers": [...]
}
```

## Процессы и потоки

### Запуск приложения

```
1. Инициализация БД (init_db.py)
   ↓
2. Загрузка .env конфигурации
   ↓
3. Создание FastAPI приложения
   ↓
4. Инициализация SQLAlchemy
   ↓
5. Регистрация маршрутов API
   ↓
6. Инициализация Aiogram бота
   ↓
7. Запуск uvicorn сервера
   ↓
8. Webhook настройка (ngrok)
```

### Обработка запроса

**HTTP запрос (Frontend → API)**:

```
1. Клиент отправляет запрос на /api/v1/surveys
   ↓
2. FastAPI маршрутизирует к surveys.py
   ↓
3. Схема валидации (Pydantic)
   ↓
4. Получение сессии БД
   ↓
5. Выполнение SQL запроса (SQLAlchemy)
   ↓
6. Сериализация результата
   ↓
7. Отправка JSON ответа
```

**Telegram сообщение (Bot)**:

```
1. Telegram отправляет webhook на /api/v1/bot/webhook
   ↓
2. Aiogram диспетчер получает обновление
   ↓
3. Маршрутизатор определяет обработчик
   ↓
4. FSM проверяет текущее состояние
   ↓
5. Обработчик выполняет логику
   ↓
6. Бот отправляет ответ
```

## Безопасность

### Защита API

- **CORS**: Ограничение доступных источников
- **Валидация**: Pydantic схемы для всех входных данных
- **SQL Injection**: SQLAlchemy ORM предотвращает SQL инъекции
- **Webhook Secret**: Валидация подписи вебхуков

### Защита бота

- **Webhook Validation**: Проверка подписи Telegram
- **Token Security**: Токен бота в .env (не в коде)
- **Input Validation**: Проверка всех входных данных

## Масштабируемость

### Текущие ограничения

- SQLite — не рекомендуется для больших нагрузок
- Single-threaded бот — ограничение на количество одновременных пользователей

### Возможности масштабирования

1. **База данных**:
   - Замена SQLite на PostgreSQL или MySQL
   - Пул соединений

2. **Бот**:
   - Использование polling вместо webhook
   - Redis для очередей сообщений

3. **API**:
   - Docker контейнеры
   - Load balancer
   - Кэширование (Redis)

## Тестирование

### Текущий подход

- Ручное тестирование через UI
- Тестирование API через curl / Swagger

### Рекомендуемый подход

- Unit тесты для сервисов
- Integration тесты для API
- E2E тесты для бота

## Документация

- **README.md** — общая документация проекта
- **API.md** — детальная документация API
- **ARCHITECTURE.md** — эта документация
- **Swagger UI** — автоматическая документация API (http://localhost:8000/docs)
