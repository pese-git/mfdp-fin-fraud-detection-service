from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from src.database.database import get_session
from src.services.crud.user import get_user_by_email, get_user_by_name, create_user
from src.services.crud.wallet import create_wallet
from src.auth.hash_password import HashPassword
from src.models.user import User
from src.models.wallet import Wallet
from src.models.role import Role


register_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@register_route.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# декоратор маршрута для входа
@register_route.post("/register", response_class=HTMLResponse)
async def register_post(request: Request, db: Session = Depends(get_session)):
    form_data = await request.form()
    errors = []
    msg = ""

    # Проверяем, что form_data содержит необходимые данные
    username = form_data.get("username")
    email = form_data.get("email")
    password = form_data.get("password")

    if username and email and password:
        try:
            # Проверка существования пользователя
            if get_user_by_name(name=username, session=db):
                raise HTTPException(
                    status_code=400, detail="Username already registered"
                )
            if get_user_by_email(email=email, session=db):
                raise HTTPException(status_code=400, detail="Email already registered")

            response = RedirectResponse("/", status.HTTP_302_FOUND)
            # Создание пользователя
            user_role = db.query(Role).filter_by(name="user").first()
            user_create = User(
                name=username,
                email=email,
                hashed_password=HashPassword().create_hash(password=password),
                role_id=user_role.id,
            )
            create_user(new_user=user_create, session=db)
            wallet_create = Wallet(balance=0, user=user_create)
            create_wallet(wallet_create, session=db)
            msg = "Register Successful!"
            print("[green]Register successful!!!!")
            return response
        except HTTPException as e:
            msg = e.detail
            errors.append(msg)
    else:
        msg = "Please provide username, email, and password."
        errors.append(msg)

    # Создаем контекст для шаблона, не используя __dict__
    context = {
        "form_data": {"msg": msg, "username": username or "", "email": email or ""},
        "request": request,
        "errors": errors,
    }

    return templates.TemplateResponse("register.html", context)
