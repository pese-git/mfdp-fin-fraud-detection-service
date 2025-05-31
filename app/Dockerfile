# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app


# Обновляем репозитории и устанавливаем необходимые системные зависимости:
# - libpq-dev: библиотека PostgreSQL, необходимая для psycopg
# - build-essential: базовые инструменты сборки (например, gcc)
# - git, curl, ca-certificates: для других зависимостей, если они нужны
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    git \
    curl \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . /app/

# Открываем порт для FastAPI приложения
EXPOSE 8000


# Установите переменную PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Команда для запуска FastAPI приложения через uvicorn
CMD ["python", "api.py"]

#CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8080"]
