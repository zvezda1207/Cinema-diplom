# Cinema Booking System — система онлайн-бронирования билетов

Дипломный проект по профессии «Веб‑разработчик: Backend-разработка на Python». Приложение включает клиентскую часть для пользователей и административную панель для управления репертуаром и продажами.

## Содержание

- [Cinema Booking System — система онлайн-бронирования билетов](#cinema-booking-system--система-онлайн-бронирования-билетов)
  - [Содержание](#содержание)
  - [Общая информация](#общая-информация)
  - [Структура репозитория](#структура-репозитория)
  - [Переменные окружения](#переменные-окружения)
  - [Развёртывание через Docker Compose](#развёртывание-через-docker-compose)
    - [Предварительные требования](#предварительные-требования)
    - [Шаги](#шаги)
    - [Остановка](#остановка)
  - [Локальная разработка](#локальная-разработка)
    - [Backend без Docker](#backend-без-docker)
    - [Frontend без Docker](#frontend-без-docker)
  - [Миграции БД](#миграции-бд)
  - [Основные функции](#основные-функции)
  - [Создание зала и генерация мест](#создание-зала-и-генерация-мест)
  - [Полезные ссылки](#полезные-ссылки)
  - [Лицензия и авторство](#лицензия-и-авторство)

## Общая информация

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL.  
- **Frontend:** React 18 (Vite), React Router, Axios.  
- **Инфраструктура:** Docker, Docker Compose.  
- **Основные сценарии:** покупка билета гостем, просмотр/архивирование бронирований, управление залами и сеансами.

## Структура репозитория

```
cinema-booking/
├── backend/                     # Серверное приложение (FastAPI)
│   ├── app/
│   │   ├── auth.py              # Аутентификация/хэширование паролей
│   │   ├── config.py            # Конфигурация и сборка DSN
│   │   ├── constants.py
│   │   ├── crud.py              # Универсальные операции с ORM
│   │   ├── dependancy.py        # Зависимости FastAPI (сессия, токен)
│   │   ├── lifespan.py          # Жизненный цикл приложения
│   │   ├── models.py            # SQLAlchemy-модели
│   │   ├── schema.py            # Pydantic-схемы запросов/ответов
│   │   └── server.py            # Основные endpoints API
│   ├── alembic/                 # Миграции БД
│   │   ├── env.py               # Конфигурация Alembic
│   │   └── versions/            # Скрипты миграций
│   ├── requirements.txt         # Python-зависимости бэкенда
│   └── Dockerfile
├── frontend/                    # Клиентское приложение (React)
│   ├── public/                  # Статические ресурсы
│   ├── src/
│   │   ├── pages/               # Страницы (Hall, Payment, Ticket, Admin и т.д.)
│   │   ├── components/          # Переиспользуемые компоненты
│   │   └── services/api.js      # Работа с API
│   ├── package.json             # JS-зависимости
│   └── Dockerfile
├── docker-compose.yml           # Описание сервисов для развёртывания
├── .env.example                 # Шаблон переменных окружения
└── README.md
```

## Переменные окружения

Создайте файл `.env` в корне проекта (можно на основе `.env.example`) и укажите значения:

```
POSTGRES_DB=cinema_example
POSTGRES_USER=cinema_user
POSTGRES_PASSWORD=cinema_password
```

Дополнительно можно переопределить значения по умолчанию для гостевого пользователя (используется при бронировании без регистрации):

```
GUEST_USER_EMAIL=no-reply@example.com
GUEST_USER_NAME=Гость
GUEST_USER_PHONE=+79991234567
GUEST_USER_PASSWORD=guest-temp
```

При запуске через Docker Compose эти переменные пробрасываются в контейнеры автоматически. Если запускаете backend локально, их нужно экспортировать в окружение вашей оболочки перед стартом сервера.

## Развёртывание через Docker Compose

### Предварительные требования

- Docker 20.10+  
- Docker Compose 2.0+

### Шаги

```bash
git clone <repository-url>
cd cinema-booking
cp .env.example .env    # либо скопировать вручную и заполнить значениями

# Сборка и запуск (foreground)
docker compose up --build

# или запуск в фоне
docker compose up -d --build
```

Сервисы будут доступны по адресам:

- Backend API: `http://localhost:8000`  
- Swagger UI: `http://localhost:8000/docs`  
- Frontend: `http://localhost:3000`  
- PostgreSQL: `localhost:15432` (в контейнере — `db:5432`)

### Остановка

```bash
docker compose down          # остановка контейнеров
docker compose down -v       # остановка + очистка volumes (удалит БД)
```

## Локальная разработка

### Backend без Docker

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Экспортируйте переменные окружения (пример для PowerShell)
$env:POSTGRES_DB = 'cinema_example'
$env:POSTGRES_USER = 'cinema_user'
$env:POSTGRES_PASSWORD = 'cinema_password'
$env:POSTGRES_HOST = 'localhost'
$env:POSTGRES_PORT = '15432'

uvicorn app.server:app --reload
```

### Frontend без Docker

```bash
cd frontend
npm install
npm run dev     # Vite dev server (порт 3000)
```

API-адрес берётся из переменной `VITE_API_URL` (по умолчанию — `http://localhost:8000`). Изменить можно в `.env` фронтенда или перед запуском:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

## Миграции БД

Для работы с Alembic активируйте виртуальное окружение бэкенда и убедитесь, что переменные среды указывают на нужную БД. Например, для локальной БД из Docker Compose:

```bash
cd backend
source .venv/bin/activate                   # или .venv\Scripts\activate

# Пример настройки окружения (PowerShell)
$env:POSTGRES_HOST = 'localhost'
$env:POSTGRES_PORT = '15432'
$env:POSTGRES_DB = 'cinema_example'
$env:POSTGRES_USER = 'cinema_user'
$env:POSTGRES_PASSWORD = 'cinema_password'

alembic upgrade head        # применить все миграции
alembic revision -m "..."   # создать новую миграцию (при изменении моделей)
```

Миграции расположены в `backend/alembic/versions/`. Актуальная схема включает поле `archived` в таблице `tickets` и дополнительные служебные миграции (`4f419bf2c3ec`, `b6c6f1d04ca9`).

## Основные функции

- Покупка билетов гостем с генерацией QR-кода и подсветкой конфликтов мест.  
- Страница оплаты с подтверждением, задержкой перехода и сообщениями об успехе.  
- Электронный билет с повторными попытками загрузки QR и подсказками.  
- Адаптивная схема зала и страниц оплаты/билета под ключевые разрешения (375 px, 768 px и т.д.).  
- Админ-панель: управление залами, фильмами, сеансами, просмотр бронирований.  
- Архивирование бронирований и автоматическая очистка архивных билетов при удалении сеанса.  
- Оптимизированный backend: кэш гостевого пользователя, асинхронная генерация QR, проверки конфликтов сеансов.

Полный перечень endpoints доступен в Swagger UI (`/docs`). Основной префикс API — `/api/v1/`.

## Создание зала и генерация мест

Администратор может создать новый зал через веб-интерфейс (раздел «Залы») или вызовом `POST /api/v1/hall`. Для быстрого поднятия окружения используйте комплект скриптов:

1. `python backend/create_admin.py` — создаёт администратора (`admin@example.com` / `admin123`) непосредственно в базе.  
2. `python backend/create_test_data.py` — авторизуется как администратор, добавляет тестовые фильмы, залы и сеансы.  
3. `python backend/generate_seats.py <hall_id>` — проходит по параметрам зала и генерирует все места, помечая центральные ряды как VIP.  
4. `python backend/update_vip_seats.py <hall_id> 4-7` — необязательный шаг для переназначения VIP-рядов (можно указать диапазон или список номеров).

Скрипты обращаются к тому же API, что и фронтенд, поэтому перед запуском убедитесь, что backend поднят и переменные окружения настроены.

## Полезные ссылки

- [FastAPI documentation](https://fastapi.tiangolo.com/)  
- [SQLAlchemy 2.0 docs](https://docs.sqlalchemy.org/en/20/)  
- [Alembic migrations](https://alembic.sqlalchemy.org/en/latest/)  
- [React 18 docs](https://react.dev/)  
- [Docker documentation](https://docs.docker.com/)

## Лицензия и авторство

Проект выполнен в учебных целях в рамках дипломной работы Нетологии.  
Автор: **Ткачева Ирина**
