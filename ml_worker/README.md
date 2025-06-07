# AntiFraud ML Worker

ML-воркер для сервиса AntiFraud: отвечает за обработку и инференс моделей машинного обучения, принимает задания по RabbitMQ, работает с БД и хранилищем артефактов (S3-совместимым).

---

## Запуск локально

### 1. Клонируйте репозиторий и перейдите в папку ml_worker

```bash
git clone ... # ваш репозиторий
cd ml_worker
```

### 2. Создайте .env

Скопируйте пример конфига и заполните своими параметрами:

```bash
cp .env.example .env
```

Отредактируйте `.env` согласно вашему окружению:  
- параметры БД (DB_HOST, DB_USER, ...)
- RabbitMQ, MLFLOW, S3 и OAuth-данные

### 3. Установите системные зависимости (Linux)

Убедитесь, что установлены build-essential, git и Python 3.10.

### 4. Установите Python-зависимости

```bash
python -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install torch==2.7.0
pip install torch-geometric==2.6.1
pip install torch-cluster==1.6.3
```

### 5. Запустите воркер

```bash
python main.py
```

---

## Запуск в Docker

### 1. Соберите образ

```bash
docker build -t antifraud-ml-worker .
```

### 2. Запустите контейнер

```bash
docker run --env-file .env antifraud-ml-worker
```

> Для интеграций (БД, RabbitMQ, S3 и пр.) убедитесь, что сервисы и сети доступны воркеру: указывайте их имена/адреса и параметры в `.env`.

---

## Переменные окружения

- `DB_*` — параметры подключения к PostgreSQL
- `RABBITMQ_*` — RabbitMQ (очереди)
- `MLFLOW_*`, `AWS_*` — используемые для MLFlow и MinIO/S3
- `OAUTH_*` — параметры авторизации через Keycloak

Все переменные смотрите и настраивайте через `.env.example`.

---

## Стандартная структура

```text
ml_worker/
  ├─ requirements.txt
  ├─ Dockerfile
  ├─ main.py
  ├─ .env.example
  └─ ...
```

---

## Примечания

- Для работы с GPU используйте собственные CUDA-образы.
- Для запуска в составе проекта — используйте общий docker-compose для подключения к сервисам.
