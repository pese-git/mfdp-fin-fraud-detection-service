from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

# from src.services.crud.predict import predict_processing
from src.auth.hash_password import HashPassword
from src.database.database import engine, init_db
from src.models.access_policy import AccessPolicy
from src.models.fin_transaction import FinTransaction
from src.models.model import Model
from src.models.role import Role
from src.models.user import User
from src.permission.access_control_middelware import AccessControlMiddleware
from src.routes.api.fin_transaction import fin_transaction_router
from src.routes.api.model import model_router
from src.routes.api.oauth import oauth_route
from src.routes.api.predict import predict_router
from src.routes.api.task import task_router
from src.routes.api.user import user_router
from src.routes.dashboard import dashboard_route
from src.routes.home import home_route
from src.routes.login import login_route
from src.routes.predict_transactions import predict_transactions_route
from src.routes.register import register_route
from src.routes.transactions_view_router import transactions_view_route
from src.routes.users import users_route
from src.services.crud.fin_transaction import create_fin_transaction
from src.services.crud.model import create_model
from src.services.crud.user import create_user
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="App")


app = FastAPI()
logger.info("FastAPI приложение инициализировано")
# Adding the AccessControlMiddleware to the app
app.add_middleware(AccessControlMiddleware)

# Jinja2 templates
template_dir = Path(__file__).parent / "src" / "templates"
templates = Jinja2Templates(directory=template_dir)

# Статические файлы
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home_route)
app.include_router(login_route)
app.include_router(dashboard_route)
app.include_router(register_route)
# app.include_router(balance_route)
app.include_router(transactions_view_route)
app.include_router(predict_transactions_route)
app.include_router(users_route)
app.include_router(oauth_route, prefix="/api/oauth")
app.include_router(user_router, prefix="/api/user")
# app.include_router(wallet_router, prefix="/api/wallet")
# app.include_router(transaction_router, prefix="/api/transaction")
app.include_router(fin_transaction_router, prefix="/api/transaction")
app.include_router(model_router, prefix="/api/model")
app.include_router(task_router, prefix="/api/tasks")
# app.include_router(balance_router, prefix="/api/balance")
app.include_router(predict_router, prefix="/api/predict")


@app.get("/error")
async def error_page(request: Request) -> Any:
    logger.warning("Пользователь перенаправлен на страницу ошибки")
    context = {"request": request}
    return templates.TemplateResponse("error.html", context)


# Обработчик исключения
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse | RedirectResponse:
    logger.error("HTTPException: %s - %s. Path: %s", exc.status_code, exc.detail, request.url.path)
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        logger.warning("403 Forbidden. Перенаправление на /error")
        return RedirectResponse(url="/error", status_code=status.HTTP_302_FOUND)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def init_data() -> None:
    try:
        logger.info("Инициализация демо-данных")
        hash_password = HashPassword()

        # --- Создание ролей ---
        with Session(engine) as session:
            admin_role = Role(name="admin")
            user_role = Role(name="user")
            session.add_all([admin_role, user_role])
            session.commit()
            session.refresh(admin_role)
            session.refresh(user_role)
            admin_role_id = admin_role.id
            user_role_id = user_role.id
            logger.info("Роли 'admin' и 'user' добавлены")

        # --- Права доступа ---
        with Session(engine) as session:
            admin_access_get = AccessPolicy(role_id=admin_role_id, resource="*", action="GET")
            admin_access_post = AccessPolicy(role_id=admin_role_id, resource="*", action="POST")
            admin_access_patch = AccessPolicy(role_id=admin_role_id, resource="*", action="PATCH")
            admin_access_put = AccessPolicy(role_id=admin_role_id, resource="*", action="PUT")
            admin_access_delete = AccessPolicy(role_id=admin_role_id, resource="*", action="DELETE")
            user_access_dashboard_get = AccessPolicy(role_id=user_role_id, resource="/dashboard", action="GET")
            user_access_predictions_get = AccessPolicy(role_id=user_role_id, resource="/transactions", action="GET")
            user_access_predict_iris_get = AccessPolicy(role_id=user_role_id, resource="/predict_fin_transaction", action="GET")
            user_access_predict_iris_post = AccessPolicy(role_id=user_role_id, resource="/predict_fin_transaction", action="POST")
            user_access_profile_get = AccessPolicy(role_id=user_role_id, resource="/api/user/profile", action="GET")
            user_access_predict_post = AccessPolicy(role_id=user_role_id, resource="/api/predict/", action="POST")
            user_access_predict_task_create_post = AccessPolicy(role_id=user_role_id, resource="/api/predict/task/create", action="POST")
            user_access_predict_task_status_get = AccessPolicy(role_id=user_role_id, resource="/api/predict/task/status/", action="GET")
            user_access_predict_task_result_get = AccessPolicy(role_id=user_role_id, resource="/api/predict/task/result/", action="GET")
            session.add_all(
                [
                    admin_access_get,
                    admin_access_post,
                    admin_access_patch,
                    admin_access_put,
                    admin_access_delete,
                    user_access_dashboard_get,
                    user_access_predictions_get,
                    user_access_predict_iris_get,
                    user_access_predict_iris_post,
                    user_access_profile_get,
                    user_access_predict_post,
                    user_access_predict_task_create_post,
                    user_access_predict_task_status_get,
                    user_access_predict_task_result_get,
                ]
            )
            session.commit()
            logger.info("Права доступа добавлены")

        # --- Пользователи ---
        with Session(engine) as session:
            admin = User(
                name="admin",
                email="admin@example.com",
                hashed_password=hash_password.create_hash("admin"),
                role_id=admin_role_id,
                is_active=True,
            )
            demo = User(
                name="demo",
                email="demo@example.com",
                hashed_password=hash_password.create_hash("demo"),
                role_id=user_role_id,
                is_active=True,
            )
            create_user(admin, session=session)
            create_user(demo, session=session)
            logger.info("Демо-пользователи admin и demo созданы")

            model = Model(
                name="PyTorch GNN",
                path="runs:/615587bb4786452e8fc4b9b8cdb69adf/model",
                is_active=True,
            )
            create_model(model, session=session)
            logger.info("Демо-модель создана")

        # --- Тестовая транзакция ---
        with Session(engine) as session:
            transaction = FinTransaction(
                TransactionID=1,
                TransactionDT=14802349,
                TransactionAmt=10.1,
                ProductCD="W",
                card1=1001,
                card2=300,
                card3=150.0,
                card4="visa",
                card5=220.0,
                card6="credit",
                addr1=330.0,
                addr2=87.0,
                dist1=2.5,
                dist2=1.3,
                P_emaildomain="gmail.com",
                R_emaildomain="yahoo.com",
                C=[10, 20, 30],
                D=[5, 2],
                M=["T", "F", None],
                V=[102, 59, 33],
                IDs=[111, 222, 333],
                isFraud=None,
                task_id=None,
            )
            create_fin_transaction(transaction, session=session)
            logger.info("Демо-транзакция добавлена")
    except Exception as e:
        logger.exception(f"Ошибка инициализации демо-данных: {e}")


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Запуск приложения: инициализация базы данных и данных")
    init_db()
    logger.info("База данных инициализирована")
    init_data()
    logger.info("Данные инициализированы")
