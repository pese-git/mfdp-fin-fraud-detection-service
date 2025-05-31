from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from src.models.user import User
from src.auth.jwt_handler import create_access_token
from src.auth.hash_password import HashPassword
from src.services.crud.user import get_user_by_email

from src.database.database import get_session
from src.database.config import get_settings

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret() -> str:
    secret_key: str = get_settings().SECRET_KEY
    return secret_key


login_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@login_route.get("/login", response_class=HTMLResponse)
async def login_get(request: Request) -> HTMLResponse:
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
) -> Any:
    errors = []
    msg = ""

    # Проверяем, что form_data не None и содержит необходимые данные
    if form_data and form_data.username and form_data.password:
        try:
            response = RedirectResponse("/dashboard", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form_data, db=db)
            msg = "Login Successful!"
            print("[green]Login successful!!!!")

            return response
        except HTTPException:
            msg = "Incorrect Email or Password"
            errors.append(msg)
    else:
        msg = "Please provide both username and password."
        errors.append(msg)

    # Создаем контекст для шаблона, инициализируя form_data если необходимо
    context = {
        "form_data": (
            form_data.__dict__ if form_data else {"msg": msg}
        ),  # Инициализация msg
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
    if user_exist is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
        )

    if user_exist.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User does not active"
        )

    access_token = create_access_token(
        {"id": user_exist.id, "email": user_exist.email, "role": user_exist.roles.name},
        secret_key=get_secret(),
    )

    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )

    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user: User = get_user_by_email(username, db)
    if not user or not HashPassword().verify_hash(password, user.hashed_password):
        return None
    return user
