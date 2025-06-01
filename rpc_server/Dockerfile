# Используем официальный образ Python
FROM python:3.10.17

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# После основного requirements
RUN pip install torch==2.7.0
RUN pip install torch-geometric==2.6.1
RUN pip install torch-cluster==1.6.3

RUN pip install pathlib

# Копируем весь код проекта в контейнер
COPY . /app/

# Запуск сервера
CMD ["python", "main.py"]
