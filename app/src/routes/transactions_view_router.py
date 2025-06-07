import json
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session


from src.models.fin_transaction import FinTransaction
from src.database.database import get_session
from src.auth.authenticate import get_current_user_via_cookies
from src.schemas import  UserRead
from src.services.logging.logging import get_logger


transactions_view_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


logger = get_logger(logger_name="routes.transactions_view")


@transactions_view_route.get("/transactions", response_class=HTMLResponse)
async def read_transactions(
    request: Request,
    db: Session = Depends(get_session),
    user: UserRead = Depends(get_current_user_via_cookies),
) -> Any:
    logger.info(
        "Пользователь '%s' (id=%s) запрашивает просмотр всех транзакций.",
        getattr(user, "name", "anonymous"),
        getattr(user, "id", "unknown")
    )

    try:
        # Получить все транзакции
        transactions = db.query(FinTransaction).all()
        logger.info("Найдено %d транзакций.", len(transactions))

        transactions_data = []
        for transaction in transactions:
            transaction_dict = {
                "created_at": transaction.created_at,
                "TransactionID": transaction.TransactionID,
                "TransactionAmt": transaction.TransactionAmt,
                "ProductCD": transaction.ProductCD,
                "card1": transaction.card1,
                "addr1": transaction.addr1,
                "C": transaction.C if transaction.C else [],
                "M": transaction.M if transaction.M else [],
                "isFraud": transaction.isFraud,
            }
            transactions_data.append(transaction_dict)

        context = {
            "request": request,
            "user": user,
            "predictions": transactions_data,
        }
        return templates.TemplateResponse("transactions.html", context)
    except Exception as e:
        logger.exception("Ошибка при получении транзакций: %s", e)
        context = {
            "request": request,
            "user": user,
            "predictions": [],
            "errors": [f"Не удалось получить транзакции: {str(e)}"],
        }
        return templates.TemplateResponse("transactions.html", context)