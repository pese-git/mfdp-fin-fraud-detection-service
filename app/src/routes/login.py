from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from src.auth.hash_password import HashPassword
from src.auth.jwt_handler import create_access_token
from src.database.config import get_settings
from src.database.database import get_session
from src.models.user import User
from src.services.crud.user import get_user_by_email
from src.services.logging.logging import get_logger

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret() -> str:
    key = get_settings().SECRET_KEY
    logger.debug("Получен SECRET_KEY для аутентификации")
    if key is None:
        raise RuntimeError("SECRET_KEY is not set in settings!")
    return key


login_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)

# Инициализация логгера для модуля авторизации
logger = get_logger(logger_name="routes.login")


@login_route.get("/login", response_class=HTMLResponse)
async def login_get(request: Request) -> HTMLResponse:
    logger.debug("Открыта страница логина (GET).")
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


# декоратор маршрута для входа
@login_route.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
    secret_key: str = Depends(get_secret),
) -> Any:
    errors = []
    msg = ""

    if form_data and form_data.username and form_data.password:
        try:
            response = RedirectResponse("/dashboard", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form_data, db=db, secret_key=secret_key)
            msg = "Login Successful!"
            logger.info("Успешный вход: пользователь '%s'", form_data.username)
            return response
        except HTTPException as exc:
            # Неудачная попытка входа по неверным данным
            msg = "Incorrect Email or Password"
            logger.warning(
                "Неудачная попытка логина для пользователя '%s'. Ошибка: %s",
                form_data.username,
                exc.detail,
            )
            errors.append(msg)
        except Exception as exc:  # [broad-exception-caught]
            msg = "Internal login error."
            logger.exception(
                "Внутренняя ошибка при попытке логина пользователя '%s': %s",
                form_data.username,
                exc,
            )
            errors.append(msg)
    else:
        msg = "Please provide both username and password."
        logger.warning("Попытка входа без имени пользователя или пароля.")
        errors.append(msg)

    context = {
        "form_data": (form_data.__dict__ if form_data else {"msg": msg}),
        "request": request,
        "errors": errors,
    }

    return templates.TemplateResponse("login.html", context)


@login_route.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
    secret_key: str = Depends(get_secret),
) -> dict[str, str]:
    user_exist = authenticate_user(db, form_data.username, form_data.password)
    logger.debug(f"#### пользователем: '{user_exist}'")
    if user_exist is None:
        logger.warning("Попытка входа с несуществующим пользователем: '%s'", form_data.username)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    if user_exist.is_active is False:
        logger.warning("Вход неактивного пользователя: '%s'", form_data.username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not active")

    if not secret_key:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Secret key not found for token generation")

    logger.debug(f"#### PWCRET KET: {secret_key}")
    access_token = create_access_token(
        {"id": user_exist.id, "email": user_exist.email, "role": user_exist.roles.name},
        secret_key=secret_key,
    )

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)

    logger.info("Пользователь '%s' успешно получил access_token.", user_exist.email)

    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_email(username, db)
    if not user:
        logger.debug("Аутентификация: пользователь '%s' не найден.", username)
        return None
    if not HashPassword().verify_hash(password, user.hashed_password):
        logger.debug("Аутентификация: неверный пароль для пользователя '%s'.", username)
        return None
    logger.debug("Аутентификация: пользователь '%s' аутентифицирован.", username)
    return user
