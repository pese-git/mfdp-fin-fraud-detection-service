from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from src import schemas
from src.auth.authenticate import get_current_user_via_cookies
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
) -> Any:
    """
    Обработчик dashboard-страницы. Добавлено логгирование успешного обращения и информации о пользователе.
    """
    # Логируем попытку обращения к dashboard и пользователя, если тот аутентифицирован
    logger.info(
        "Пользователь '%s' (id=%s) обратился к /dashboard",
        getattr(current_user, "name", "anonymous"),
        getattr(current_user, "id", "unknown"),
    )
    context = {"user": current_user, "username": current_user.name, "request": request}
    return templates.TemplateResponse("dashboard.html", context)
