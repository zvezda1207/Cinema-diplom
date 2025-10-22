# Cinema Booking System - Система бронирования билетов в кинотеатр

Дипломный проект по профессии «Веб-разработчик: Backend-разработка на Python»

## Описание проекта

Комплексное веб-приложение для онлайн бронирования билетов в кинотеатр с административной панелью для управления залами, сеансами и бронированиями.

### Технологический стек

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Alembic (миграции)
- Uvicorn (ASGI сервер)

**Frontend:**
- React 18
- React Router
- Axios
- CSS3

**DevOps:**
- Docker
- Docker Compose

## Структура проекта

```
cinema-booking/
├── backend/              # Backend приложение (FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── server.py    # Основной файл приложения
│   │   └── database.py  # Настройка подключения к БД
│   ├── models.py        # Модели SQLAlchemy
│   ├── requirements.txt # Python зависимости
│   └── Dockerfile
├── frontend/            # Frontend приложение (React)
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml   # Оркестрация сервисов
└── README.md
```

## Модели данных

- **Hall** - кинозалы
- **Seat** - места в залах
- **Movie** - фильмы
- **Session** - сеансы
- **Booking** - бронирования
- **User** - администраторы

## Установка и запуск

### Предварительные требования

- Docker 20.10+
- Docker Compose 2.0+

### Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd cinema-booking
```

### Шаг 2: Создание .env файла

Создайте файл `.env` в корне проекта на основе `.env.example`:

```bash
# На Linux/Mac
cp .env.example .env

# На Windows PowerShell
Copy-Item .env.example .env
```

Содержимое `.env`:
```env
POSTGRES_DB=cinema_booking
POSTGRES_USER=cinema_user
POSTGRES_PASSWORD=cinema_password_2024
```

### Шаг 3: Запуск приложения

```bash
# Сборка и запуск всех контейнеров
docker-compose up --build

# Или в фоновом режиме
docker-compose up -d --build
```

### Шаг 4: Проверка работы

- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Frontend:** http://localhost:3000
- **PostgreSQL:** localhost:5434

### Остановка приложения

```bash
# Остановка контейнеров
docker-compose down

# Остановка с удалением volumes (БД будет очищена!)
docker-compose down -v
```

## Разработка

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.server:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## API Endpoints

### Публичные
- `GET /` - Welcome message
- `GET /health` - Health check

### Планируемые endpoints
- `GET /api/movies` - Список фильмов
- `GET /api/sessions` - Список сеансов
- `POST /api/bookings` - Создание бронирования
- `GET /api/halls/{id}/seats` - Места в зале

### Административные (требуют авторизации)
- `POST /api/admin/halls` - Создание зала
- `PUT /api/admin/halls/{id}` - Редактирование зала
- `POST /api/admin/sessions` - Создание сеанса
- `GET /api/admin/bookings` - Список бронирований

## Функциональность

### Пользовательская часть
- Просмотр списка фильмов и сеансов
- Выбор места в зале
- Бронирование билета
- Получение кода бронирования

### Административная часть
- Управление залами (создание, редактирование, активация/деактивация)
- Настройка мест в залах
- Управление фильмами
- Создание сеансов
- Просмотр бронирований
- Управление продажами билетов

## Лицензия

Проект создан в образовательных целях в рамках дипломного проекта Нетология.

## Автор

[Ваше имя]

## Ссылки

- [Задание дипломного проекта](https://github.com/netology-code/fsmidpd-diplom)


