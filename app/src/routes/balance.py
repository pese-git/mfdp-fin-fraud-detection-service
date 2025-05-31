from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.models.transaction import Transaction
from src.database.database import get_session
from src.auth.authenticate import get_current_user_via_cookies
from src.services.crud.balance import update_balance_by_user_id
from src.models.user import User

balance_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@balance_route.get("/balance", response_class=HTMLResponse)
async def redirect_read_user_balance_view(
    request: Request,
    db: Session = Depends(get_session),
    curr_user: User = Depends(get_current_user_via_cookies),
) -> RedirectResponse:
    return RedirectResponse(url=f"/balance/{curr_user.id}", status_code=301)
    

@balance_route.get("/balance/{id}", response_class=HTMLResponse)
async def read_user_balance_view(
    request: Request,
    id: int,
    db: Session = Depends(get_session),
    curr_user: User = Depends(get_current_user_via_cookies),
) -> HTMLResponse:
    if curr_user.roles.name == "admin":
        user_id = id if id is not None else curr_user.id
    else:
        user_id = curr_user.id
    # Извлечение транзакций пользователя
    user = db.query(User).filter(User.id == user_id).first()
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()

    # Создание контекста шаблона
    context = {
        "request": request,
        "user": user,
        "transactions": transactions,
    }
    return templates.TemplateResponse("balance.html", context)


@balance_route.get("/balance/recharge/{id}", response_class=HTMLResponse)
async def read_user_balance_recharge(
    request: Request,
    id: int,
    db: Session = Depends(get_session),
    curr_user: User = Depends(get_current_user_via_cookies),
) -> HTMLResponse:
    if curr_user.roles.name == "admin":
        user_id = id if id is not None else curr_user.id
    else:
        user_id = curr_user.id
    # Извлечение транзакций пользователя
    user = db.query(User).filter(User.id == user_id).first()

    context = {"request": request, "user": user}
    return templates.TemplateResponse("recharge.html", context)


@balance_route.post("/balance/recharge/{id}", response_class=HTMLResponse)
async def recharge_user_balance(
    request: Request,
    id: int,
    amount: int = Form(...),
    db: Session = Depends(get_session),
    curr_user: User = Depends(get_current_user_via_cookies),
) -> HTMLResponse:
    if curr_user.roles.name == "admin":
        user_id = id if id is not None else curr_user.id
    else:
        user_id = curr_user.id
    print(f"Select user id: {user_id}")
    # Извлечение транзакций пользователя
    user = db.query(User).filter(User.id == user_id).first()

    errors = []
    message = ""

    try:
        if amount < 1:
            raise HTTPException(
                status_code=400, detail="Сумма должна быть положительным числом."
            )

        # user.wallet.balance += amount
        update_balance_by_user_id(user_id=user_id, amount=amount, session=db)
        db.commit()
        message = f"Ваш баланс успешно пополнен на {amount} кредитов."
    except HTTPException as e:
        errors.append(e.detail)

    context = {"request": request, "user": user, "errors": errors, "message": message}
    return templates.TemplateResponse("recharge.html", context)
