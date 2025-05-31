# MFDP Financial Fraud Detection Service

## О сервисе

Данный проект — микросервис для детектирования мошеннических (фродовых) событий в финансовых транзакциях. Он построен на базе FastAPI, Postgres, Nginx и поддерживает дальнейшее развитие, включая интеграцию с ML-модулями и брокерами сообщений.

## Структура репозитория

```
.
├── app/            # Код сервиса (FastAPI, бизнес-логика, шаблоны)
├── nginx/          # Конфигурация Nginx
├── postgres_data/  # Данные PostgreSQL (volume)
├── docker-compose.yaml
├── README.md
└── webview/        # Возможная поддержка web/dashboards
```

## Запуск сервиса в Docker

1. **Склонируйте репозиторий**
   ```bash
   git clone https://github.com/your-org/mfdp-fin-fraud-detection-service.git
   cd mfdp-fin-fraud-detection-service
   ```

2. **Создайте файл окружения для приложения**

   В папке `app/` создайте файл `.env` со следующим содержимым (приведён пример, значения измените под себя):

   ```
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=sa
   SECRET_KEY=your_secret_key
   ```

3. **Запустите сервисы через Docker Compose**
   ```bash
   docker-compose up --build
   ```

   Это поднимет три контейнера:
   - **app** (FastAPI anti-fraud сервис)
   - **db** (PostgreSQL)
   - **web** (Nginx reverse-proxy на 80/443 портах)

4. **Доступ к приложениям:**
   - API/веб-интерфейс: [http://localhost](http://localhost)
   - Документация Swagger (если подключена): [http://localhost/docs](http://localhost/docs)

## Остановка и удаление

Для остановки контейнеров:
```bash
docker-compose down
```

Удалить volume с БД (полностью очистить данные):
```bash
docker-compose down -v
```

## Примечания

- После первого запуска может потребоваться время на инициализацию БД.
- Автоматические миграции не подключены — инициализация структуры таблиц происходит через alembic/ORM (см. документацию в `/app/database/`).

## Разработка

Для локальной разработки можно использовать виртуальное окружение, установить зависимости из `app/requirements.txt` и запускать приложение напрямую через uvicorn.

## Обратная связь

Для вопросов и предложений открывайте Issue или пишите в дискуссиях репозитория.