import json
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlmodel import Session

from src.models.user import User
from src.database.database import get_session
from src.auth.authenticate import get_current_user_via_cookies

from src.services.crud.user import update_user
from src.services.logging.logging import get_logger


users_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


logger = get_logger(logger_name="routes.users")


@users_route.get("/users", response_class=HTMLResponse)
async def read_users(
    request: Request,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user_via_cookies),
) -> Any:
    logger.info("Пользователь '%s' (id=%s) смотрит список пользователей.",
                getattr(user, "name", "anonymous"), getattr(user, "id", "unknown"))
    users = db.query(User).all()
    logger.debug("Получено пользователей: %d", len(users))
    context = {
        "request": request,
        "user": user,
        "users": users,
    }
    return templates.TemplateResponse("users.html", context)


@users_route.get("/user/{id}", response_class=HTMLResponse)
async def start_edit_user(
    request: Request,
    id: int,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user_via_cookies),
) -> Any:
    logger.info("Пользователь '%s' (id=%s) открывает форму редактирования пользователя c id=%s.",
                getattr(user, "name", "anonymous"), getattr(user, "id", "unknown"), id)
    edit_user = db.query(User).filter_by(id=id).first()
    if not edit_user:
        logger.warning("Пользователь c id=%s не найден для редактирования.", id)
    context = {
        "request": request,
        "user": user,
        "edit_user": edit_user,
    }
    return templates.TemplateResponse("user_edit.html", context)


@users_route.post("/user/{id}", response_class=HTMLResponse)
async def end_edit_user(
    request: Request,
    id: int,
    name: str = Form(...),
    email: EmailStr = Form(...),
    is_active: str = Form(default="off"),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user_via_cookies),
) -> Any:
    errors = []
    message = ""

    try:
        edit_user: User = db.query(User).filter_by(id=id).first()
        logger.info("Попытка обновить пользователя id=%s (старое имя: '%s', новое имя: '%s').",
                    id, getattr(edit_user, "name", "не найден"), name)

        edit_user.name = name
        edit_user.email = email
        edit_user.is_active = is_active == "on"

        update_user(user=edit_user, session=db)
        message = "User updated successfully."
        logger.info("Пользователь id=%s успешно обновлён.", id)

        return RedirectResponse(url="/users", status_code=status.HTTP_302_FOUND)

    except HTTPException as e:
        errors.append(e.detail)
        message = e.detail
        logger.warning("Ошибка при обновлении пользователя id=%s: %s", id, e.detail)
        context = {
            "request": request,
            "user": user,
            "edit_user": edit_user,
            "errors": errors,
            "message": message,
        }
        return templates.TemplateResponse("user_edit.html", context)
    except Exception as e:
        message = "Internal server error."
        logger.exception("Внутренняя ошибка при обновлении пользователя id=%s: %s", id, str(e))
        context = {
            "request": request,
            "user": user,
            "edit_user": None,
            "errors": [message],
            "message": message,
        }
        return templates.TemplateResponse("user_edit.html", context)