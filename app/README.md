# AntiFraud App Service

Сервис для анализа, мониторинга и выявления мошеннических транзакций.
Включает дашборд пользователя с графиками и статистикой.

---

## Быстрый старт

Проект можно запустить локально или в Docker.

---

## 1. Запуск локально

### 1.1. Установите зависимости

```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
# venv\Scripts\activate   # Для Windows

pip install -r requirements.txt
```

### 1.2. Создайте файл окружения

Скопируйте `.env.example` и настройте `.env` по своему окружению (пример уже есть в `app/.env.example`).

### 1.3. Убедитесь, что у вас есть PostgreSQL и RabbitMQ

- Запустите PostgreSQL и создайте базу, пользователя с паролем, как в `.env`.
- Убедитесь, что RabbitMQ запущен (локально или в контейнере) и его параметры соответствуют `.env`:
  - `RABBITMQ_HOST`, `RABBITMQ_QUEUE`, `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS`

### 1.4. Примените миграции (при необходимости)

> Проект использует SQLModel/SQLAlchemy — миграции могут применяться через Alembic или вручную.
> Убедитесь, что таблицы созданы до первого запуска.

### 1.5. Запустите сервис

```bash
export PYTHONPATH=src
python api.py
# или через uvicorn если используется FastAPI
# uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### 1.6. Откройте сервис

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000) в браузере.

---

## 2. Запуск через Docker

### 2.1. Соберите образ

```bash
docker build -t antifraud-app .
```

### 2.2. Запустите контейнер

```bash
docker run --env-file app/.env -p 8000:8000 antifraud-app
```

- Если используется внешняя БД или RabbitMQ — убедитесь, что параметры подключения указаны в `.env` и видны из контейнера.
- Для полноценного запуска с PostgreSQL и RabbitMQ используйте docker-compose (пример ниже).

### 2.3. Откройте сервис

Откройте [http://localhost:8000](http://localhost:8000) в браузере.

---

## 3. О переменных окружения

Файл `.env` содержит чувствительные параметры:

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASS` — параметры подключения к БД PostgreSQL.
- `SECRET_KEY` — секретный ключ для токенов.
- `RABBITMQ_HOST`, `RABBITMQ_QUEUE`, `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` — используются для связи с RabbitMQ (сервис брокера очередей).
  - Убедитесь, что сервис RabbitMQ доступен и параметры соответствуют вашему окружению.

---

## 4. Структура проекта

```text
app/
  ├─ src/
  │    ├─ api.py           # Точка входа FastAPI
  │    ├─ models/          # Модели SQLModel
  │    ├─ routes/          # Роутеры FastAPI
  │    ├─ templates/       # Jinja2 Templates
  │    └─ ...
  ├─ requirements.txt
  ├─ Dockerfile
  └─ .env
```

---

## 5. Пример типовых команд Docker

```bash
# Сборка образа
docker build -t antifraud-app .

# Запуск контейнера на 8000 порту с переменными из .env
docker run --env-file app/.env -p 8000:8000 antifraud-app
```

---

## 6. Docker Compose (пример)

Для удобства можно создать файл `docker-compose.yml` примерно такого содержания:

```yaml
version: '3.7'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: sa
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    ports:
      - "5672:5672"
      - "15672:15672"

  app:
    build: .
    image: antifraud-app
    env_file:
      - app/.env
    ports:
      - "8000:8000"
    depends_on:
      - db
      - rabbitmq
```

---

## 7. Вопросы и доработки

- Убедитесь, что база данных и RabbitMQ доступны сервису (`host.docker.internal` или имена сервисов в docker-compose).
- Для миграций используйте Alembic.
