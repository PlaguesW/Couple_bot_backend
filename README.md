# Couple Bot Backend API

REST API для приложения "Couple Bot" - бота для планирования свиданий парами.

## Возможности

- **Управление пользователями**: Регистрация и получение информации о пользователях
- **Управление парами**: Создание пар, присоединение по коду приглашения
- **Управление идеями**: CRUD операции для идей свиданий
- **Управление событиями**: Создание предложений свиданий, ответы на них, история

## Структура проекта

```
couple_bot_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              
│   ├── config.py            
│   ├── database.py          
│   ├── schemas/            
│   │   ├── user.py
│   │   ├── couple.py
│   │   ├── idea.py
│   │   └── date_event.py
│   └── routers/            
│       ├── auth.py          
│       ├── users.py        
│       ├── couples.py       
│       ├── ideas.py        
│       └── dates.py        
├── requirements.txt
├── .env.example
└── README.md
```

## Установка и запуск

### 1. Клонирование и установка зависимостей

```bash
git clone <repository-url>
cd couple_bot_backend
pip install -r requirements.txt
```

### 2. Настройка окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл с вашими настройками:

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DB_NAME
DEBUG=True
APP_NAME=Couple Bot API
APP_VERSION=1.0.0
```

### 3. Настройка базы данных

Убедитесь, что PostgreSQL запущен и создана база данных:

```sql
CREATE DATABASE couple_bot;
```

### 4. Запуск приложения

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

## API Документация

После запуска приложения доступна автоматическая документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Основные эндпоинты

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация пользователя

### Пользователи
- `GET /api/v1/users/` - Получить всех пользователей
- `GET /api/v1/users/{user_id}` - Получить пользователя по ID

### Пары
- `POST /api/v1/couples/` - Создать пару
- `POST /api/v1/couples/join` - Присоединиться к паре
- `GET /api/v1/couples/{couple_id}` - Получить информацию о паре
- `GET /api/v1/couples/code/{invite_code}` - Генерировать код приглашения

### Идеи для свиданий
- `GET /api/v1/ideas/` - Получить все идеи
- `POST /api/v1/ideas/` - Создать новую идею
- `GET /api/v1/ideas/{idea_id}` - Получить конкретную идею
- `PATCH /api/v1/ideas/{idea_id}` - Обновить идею
- `DELETE /api/v1/ideas/{idea_id}` - Удалить идею

### События (свидания)
- `POST /api/v1/dates/proposal` - Предложить свидание
- `POST /api/v1/dates/respond` - Ответить на предложение
- `GET /api/v1/dates/history/{couple_id}` - История свиданий пары
- `GET /api/v1/dates/{event_id}` - Получить конкретное событие

## Схема базы данных

### Таблицы:

1. **users** - Пользователи
   - id (SERIAL PRIMARY KEY)
   - telegram_id (BIGINT UNIQUE)
   - name (VARCHAR(255))
   - username (VARCHAR(255))
   - created_at, updated_at (TIMESTAMP)

2. **couples** - Пары
   - id (SERIAL PRIMARY KEY)
   - user1_id, user2_id (INTEGER REFERENCES users(id))
   - invite_code (VARCHAR(6) UNIQUE)
   - created_at (TIMESTAMP)

3. **ideas** - Идеи для свиданий
   - id (SERIAL PRIMARY KEY)
   - title (VARCHAR(255))
   - description (TEXT)
   - category (VARCHAR(100))
   - is_active (BOOLEAN)
   - created_at (TIMESTAMP)

4. **date_events** - События/предложения свиданий
   - id (SERIAL PRIMARY KEY)
   - couple_id (INTEGER REFERENCES couples(id))
   - idea_id (INTEGER REFERENCES ideas(id))
   - proposer_id (INTEGER REFERENCES users(id))
   - date_status (VARCHAR(20)) - pending/accepted/rejected
   - scheduled_date, completed_date (TIMESTAMP)
   - created_at (TIMESTAMP)

### Запуск в режиме разработки:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
