from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from src.auth.hash_password import HashPassword
from src.database.database import get_session
from src.models.role import Role
from src.models.user import User
from src.services.crud.user import create_user, get_user_by_email, get_user_by_name
from src.services.logging.logging import get_logger

register_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

# Инициализация логгера
logger = get_logger(logger_name="routes.register")


@register_route.get("/register")
async def register_form(request: Request) -> Any:
    logger.debug("Открыта страница регистрации (GET).")
    return templates.TemplateResponse("register.html", {"request": request})


@register_route.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, db: Session = Depends(get_session)) -> Any:
    form_data = await request.form()
    errors = []
    msg = ""

    username = form_data.get("username")
    email = form_data.get("email")
    password = form_data.get("password")

    if not isinstance(username, str):
        errors.append("Имя пользователя указано неверно")
        username = None
    if not isinstance(email, str):
        errors.append("Email указан неверно")
        email = None
    if not isinstance(password, str):
        errors.append("Пароль указан неверно")
        password = None

    logger.debug("Попытка регистрации: username='%s', email='%s'", username, email)

    if username and email and password:
        try:
            if get_user_by_name(name=username, session=db):
                logger.warning("Попытка регистрации с уже существующим username: '%s'", username)
                errors.append("Username already registered")
                raise HTTPException(status_code=400, detail="Username already registered")
            if get_user_by_email(email=email, session=db):
                logger.warning("Попытка регистрации с уже существующим email: '%s'", email)
                errors.append("Email already registered")
                raise HTTPException(status_code=400, detail="Email already registered")

            user_role = db.query(Role).filter_by(name="user").first()
            if not user_role:
                msg = "Роль 'user' не найдена в базе данных."
                logger.error(msg)
                errors.append(msg)
                context = {
                    "form_data": {"msg": msg, "username": username or "", "email": email or ""},
                    "request": request,
                    "errors": errors,
                }
                return templates.TemplateResponse("register.html", context)

            user_create = User(
                name=username,
                email=email,
                hashed_password=HashPassword().create_hash(password=password),
                role_id=user_role.id,
            )
            create_user(new_user=user_create, session=db)
            msg = "Register Successful!"
            logger.info("Успешная регистрация пользователя: '%s'", username)
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            return response

        except HTTPException as e:
            msg = e.detail
            errors.append(msg)
            logger.warning("Ошибка регистрации пользователя '%s': %s", username, msg)
        except Exception as e:
            msg = "Internal registration error."
            errors.append(msg)
            logger.exception("Внутренняя ошибка при регистрации пользователя '%s': %s", username, e)
    else:
        msg = "Please provide username, email, and password."
        errors.append(msg)
        logger.warning(
            "Попытка регистрации с неполными данными. username='%s', email='%s'",
            username,
            email,
        )

    context = {
        "form_data": {"msg": msg, "username": username or "", "email": email or ""},
        "request": request,
        "errors": errors,
    }

    return templates.TemplateResponse("register.html", context)
