FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/

# [1] Установить системные dev-пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*
    
# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# После основного requirements
RUN pip install torch==2.7.0
RUN pip install torch-geometric==2.6.1
RUN pip install torch-cluster==1.6.3

CMD ["python", "main.py"]