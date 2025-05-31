from pathlib import Path
import re
from typing import Any
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from src.auth.jwt_handler import verify_access_token
from src.models.access_policy import AccessPolicy
from src.models.role import Role
from src.permission.access_control_middelware import AccessControlMiddleware
from src.routes.home import home_route
from src.routes.api.oauth import oauth_route
from src.routes.api.user import user_router
from src.routes.api.prediction import prediction_router
from src.routes.api.task import task_router
from src.routes.api.model import model_router
from src.routes.api.predict import predict_router
from src.routes.login import login_route
from src.routes.dashboard import dashboard_route
from src.routes.register import register_route
from src.routes.predictions import predictions_route
from src.routes.predict_iris import predict_iris_route
from src.routes.users import users_route
from src.database.database import get_session, init_db, engine
from src.models.user import User
from src.models.model import Model
from src.services.crud.user import create_user
from src.services.crud.model import create_model
from src.services.crud.predict import predict_processing
from src.auth.hash_password import HashPassword


from src.database.config import get_settings


from jose import jwt, exceptions

app = FastAPI()
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
#app.include_router(balance_route)
app.include_router(predictions_route)
app.include_router(predict_iris_route)
app.include_router(users_route)
app.include_router(oauth_route, prefix="/api/oauth")
app.include_router(user_router, prefix="/api/user")
#app.include_router(wallet_router, prefix="/api/wallet")
#app.include_router(transaction_router, prefix="/api/transaction")
app.include_router(prediction_router, prefix="/api/prediction")
app.include_router(model_router, prefix="/api/model")
app.include_router(task_router, prefix="/api/tasks")
#app.include_router(balance_router, prefix="/api/balance")
app.include_router(predict_router, prefix="/api/predict")


@app.get("/error")
async def error_page(request: Request) -> Any:
    context = {"request": request}
    return templates.TemplateResponse("error.html", context)


# Обработчик исключения
@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse | RedirectResponse:
    # Проверяем, является ли статус 403
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        return RedirectResponse(url="/error", status_code=status.HTTP_302_FOUND)
    # Если другой статус, возвращаем стандартный ответ
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def init_data() -> None:
    try:
        hash_password = HashPassword()
        with Session(engine) as session:
            admin_role = Role(name="admin")
            user_role = Role(name="user")
            session.add_all([admin_role, user_role])
            session.commit()
            # session.refresh()

        with Session(engine) as session:
            admin_access_get = AccessPolicy(role=admin_role, resource="*", action="GET")
            admin_access_post = AccessPolicy(
                role=admin_role, resource="*", action="POST"
            )
            admin_access_patch = AccessPolicy(
                role=admin_role, resource="*", action="PATCH"
            )
            admin_access_put = AccessPolicy(role=admin_role, resource="*", action="PUT")
            admin_access_delete = AccessPolicy(
                role=admin_role, resource="*", action="DELETE"
            )
            user_access_dashboard_get = AccessPolicy(
                role=user_role, resource="/dashboard", action="GET"
            )
            user_access_predictions_get = AccessPolicy(
                role=user_role, resource="/predictions", action="GET"
            )
            user_access_predict_iris_get = AccessPolicy(
                role=user_role, resource="/predict_iris", action="GET"
            )
            user_access_predict_iris_post = AccessPolicy(
                role=user_role, resource="/predict_iris", action="POST"
            )

            user_access_profile_get = AccessPolicy(
                role=user_role, resource="/api/user/profile", action="GET"
            )

            user_access_predict_post = AccessPolicy(
                role=user_role, resource="/api/predict/", action="POST"
            )

            user_access_predict_task_create_post = AccessPolicy(
                role=user_role, resource="/api/predict/task/create", action="POST"
            )

            user_access_predict_task_status_get = AccessPolicy(
                role=user_role, resource="/api/predict/task/status/", action="GET"
            )

            user_access_predict_task_result_get = AccessPolicy(
                role=user_role, resource="/api/predict/task/result/", action="GET"
            )

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

        with Session(engine) as session:
            admin = User(
                name="admin",
                email="admin@example.com",
                hashed_password=hash_password.create_hash("admin"),
                roles=admin_role,
            )
            demo = User(
                name="demo",
                email="demo@example.com",
                hashed_password=hash_password.create_hash("demo"),
                roles=user_role,
            )
            create_user(admin, session=session)
            create_user(demo, session=session)

            model = Model(name="chatgpt-o4", path="model from")
            create_model(model, session=session)

        with Session(engine) as session:
            predict_processing(
                user_id=1, model="chatgpt-o4", input_data="Hello world", session=session
            )
    except Exception as e:
        print(f"Error: {e}")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    init_data()
