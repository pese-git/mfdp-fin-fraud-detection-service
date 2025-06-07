import json
from pathlib import Path
from typing import Any
from fastapi import APIRouter, HTTPException, Request, Form, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.models.model import Model
from src.models.task import Task
from src.database.database import get_session
from src.auth.authenticate import get_current_user_via_cookies
from src.schemas import UserRead

from src.routes.api.predict import PredictionCreate

from uuid import uuid4
from src.services.rm.rm import RabbitMQClient, RabbitMQConfig
from src.services.logging.logging import get_logger


rabbitmq_config = RabbitMQConfig()  # или из env/настроек
rabbitmq_client = RabbitMQClient(rabbitmq_config)

predict_transactions_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

# Инициализация логгера для predict_transactions
logger = get_logger(logger_name="routes.predict_transactions")


def nan_to_none(x) -> Any | None:
    import pandas as pd
    if pd.isna(x):
        return None
    return x


def row_to_prediction_dict(row):
    return {
        "TransactionID": int(row["TransactionID"]),
        "TransactionDT": int(row["TransactionDT"]),
        "TransactionAmt": float(row["TransactionAmt"]),
        "ProductCD": nan_to_none(row["ProductCD"]),
        "card1": nan_to_none(row.get("card1")),
        "card2": nan_to_none(row.get("card2")),
        "card3": nan_to_none(row.get("card3")),
        "card4": nan_to_none(row.get("card4")),
        "card5": nan_to_none(row.get("card5")),
        "card6": nan_to_none(row.get("card6")),
        "addr1": nan_to_none(row.get("addr1")),
        "addr2": nan_to_none(row.get("addr2")),
        "dist1": nan_to_none(row.get("dist1")),
        "dist2": nan_to_none(row.get("dist2")),
        "P_emaildomain": nan_to_none(row.get("P_emaildomain")),
        "R_emaildomain": nan_to_none(row.get("R_emaildomain")),
        "C": [nan_to_none(row.get(f"C{i}")) for i in range(1, 15)],
        "D": [nan_to_none(row.get(f"D{i}")) for i in range(1, 16)],
        "M": [nan_to_none(row.get(f"M{i}")) for i in range(1, 10)],
        "V": [nan_to_none(row.get(f"V{i}")) for i in range(1, 340)],
        "id": [nan_to_none(row.get(f"id_{str(i).zfill(2)}")) for i in range(1, 28)],
    }



@predict_transactions_route.get("/predict_fin_transaction", response_class=HTMLResponse)
async def read_predict_fin_transaction(
    request: Request,
    task_id: str = None,
    db: Session = Depends(get_session),
    user: UserRead = Depends(get_current_user_via_cookies),
) -> HTMLResponse:
    predictions = None
    errors = []
    status = None

    if task_id:
        logger.info(  # Логируем попытку получения статуса задачи
            "Пользователь '%s' (id=%s) запрашивает статус задачи '%s'",
            getattr(user, "name", "anonymous"),
            getattr(user, "id", "unknown"),
            task_id
        )
        task = db.query(Task).filter(Task.task_id == task_id).first()
        if task is None:
            errors.append(f"Task with ID '{task_id}' not found.")
            status = "not_found"
            logger.warning("Task с ID '%s' не найден.", task_id)
        else:
            status = task.status
            if task.status == "success":
                predictions = task.fintransaction
                logger.info("Task '%s' завершена успешно.", task_id)
            elif task.status == "error":
                errors.append(f"Task завершилась с ошибкой: {task.error or task}")
                logger.error("Task '%s' завершилась с ошибкой: %s", task_id, task.error)
            else:
                errors.append(f"Task в статусе: {task.status}")
                logger.info("Task '%s' в статусе: %s", task_id, task.status)

    context = {
        "request": request,
        "user": user,
        "task_id": task_id,
        "predictions": predictions,
        "errors": errors,
        "status": status,
    }
    return templates.TemplateResponse("predict_transactions.html", context)


@predict_transactions_route.post("/predict_fin_transaction", response_class=HTMLResponse)
async def predict_fin_transaction(
    request: Request,
    transaction_csv: str = Form(...),
    db: Session = Depends(get_session),
    user: UserRead = Depends(get_current_user_via_cookies),
) -> HTMLResponse:
    errors = []
    task_id = str(uuid4())

    logger.info(
        "Поступил запрос на предсказание финансовой транзакции от пользователя '%s' (id=%s). Task ID: %s",
        getattr(user, "name", "anonymous"),
        getattr(user, "id", "unknown"),
        task_id
    )

    try:
        import pandas as pd
        from io import StringIO

        df = pd.read_csv(StringIO(transaction_csv.strip()))
        prediction_inputs = []
        for row in df.to_dict(orient="records"):
            pred_dict = row_to_prediction_dict(row)
            prediction_inputs.append(pred_dict)

        # Сохраняем задачу в базу данных со статусом "init"
        model = db.query(Model).first()
        if not model:
            logger.error("Model not found при создании задачи task_id=%s", task_id)
            raise Exception("Model not found")
        task = Task(
            task_id=task_id, 
            status="init",
            model=model
        )

        # Отправляем задачу через RabbitMQ
        queue_task = {
            "task_id": task_id,
            "input_data": prediction_inputs,
        }
        ok = rabbitmq_client.send_task(queue_task)
        if not ok:
            logger.error("Не удалось отправить задачу task_id=%s в очередь.", task_id)
            raise Exception("Не удалось отправить задачу в очередь.")

        db.add(task)
        db.commit()
        logger.info("Задача task_id=%s успешно добавлена и поставлена в очередь.", task_id)
    except Exception as e:
        db.rollback()
        errors.append(str(e))
        logger.exception(
            "Ошибка при обработке запроса предсказания для пользователя '%s' (task_id=%s): %s",
            getattr(user, "name", "anonymous"),
            task_id,
            e
        )

    # После постановки задачи редиректим на страницу результатов с task_id
    url = request.url_for("read_predict_fin_transaction").include_query_params(task_id=task_id)
    from starlette.responses import RedirectResponse
    return RedirectResponse(url, status_code=303)