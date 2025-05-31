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


users_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@users_route.get("/users", response_class=HTMLResponse)
async def read_users(
    request: Request,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user_via_cookies),
) -> Any:
    # Извлечь историю предсказаний пользователя
    users = db.query(User).all()

    # Создание контекста для шаблона
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
    # Извлечь историю предсказаний пользователя
    edit_user = db.query(User).filter_by(id=id).first()

    # Создание контекста для шаблона
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
        # Извлечь историю предсказаний пользователя
        edit_user: User = db.query(User).filter_by(id=id).first()
        edit_user.name = name
        edit_user.email = email
        edit_user.is_active = is_active == "on"

        # user.wallet.balance += amount
        update_user(user=edit_user, session=db)
        message = "User updated successfully."

        return RedirectResponse(url="/users", status_code=status.HTTP_302_FOUND)

    except HTTPException as e:
        errors.append(e.detail)
        message = e.detail

        context = {
            "request": request,
            "user": user,
            "edit_user": edit_user,
            "errors": errors,
            "message": message,
        }
        return templates.TemplateResponse("user_edit.html", context)
