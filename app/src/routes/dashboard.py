from pathlib import Path
from typing import Any

from database.database import get_session
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from src import schemas
from src.auth.authenticate import get_current_user_via_cookies
from src.models.fin_transaction import FinTransaction
from src.services.logging.logging import get_logger

dashboard_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


# Инициализация логгера для этого модуля
logger = get_logger(logger_name="routes.dashboard")


@dashboard_route.get("/dashboard")
async def read_dashboard(
    request: Request,
    current_user: schemas.UserBase = Depends(get_current_user_via_cookies),
    db: Session = Depends(get_session),
) -> Any:
    """
    Обработчик dashboard-страницы. Выводит статистику транзакций.
    """
    logger.info(
        "Пользователь '%s' (id=%s) обратился к /dashboard",
        getattr(current_user, "name", "anonymous"),
        getattr(current_user, "id", "unknown"),
    )

    # Статистика по транзакциям
    total_count = db.query(FinTransaction).count()
    fraud_count = db.query(FinTransaction).filter(FinTransaction.isFraud == 1).count()  # type: ignore
    good_count = db.query(FinTransaction).filter(FinTransaction.isFraud == 0).count()  # type: ignore

    context = {
        "user": current_user,
        "username": current_user.name,
        "request": request,
        "total_count": total_count,
        "fraud_count": fraud_count,
        "good_count": good_count,
    }
    return templates.TemplateResponse("dashboard.html", context)
