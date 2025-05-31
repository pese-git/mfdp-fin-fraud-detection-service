from pathlib import Path
from typing import Any
from fastapi import APIRouter, HTTPException, Request, Form, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.services.rpc.rpc_client import RpcClient
from src.database.database import get_session
from src.auth.authenticate import get_current_user_via_cookies
from src.schemas import User


from src.routes.api.predict import predict as predict_processing
from src.routes.api.predict import PredictionCreate

predict_iris_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


def get_rpc() -> RpcClient:
    return RpcClient()


def make_rpc_call(rpc: RpcClient) -> Any:
    def callback(input_data: dict[str, Any]) -> Any:
        print(f" [x] Запрос на вычисление ({input_data})")
        result = rpc.call(input_data)
        print(f" [.] Получен ответ: {result}")
        return result

    return callback


# Словарь для отображения числовых предсказаний в текстовые названия
iris_map = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}


@predict_iris_route.get("/predict_iris", response_class=HTMLResponse)
async def read_balance(
    request: Request,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user_via_cookies),
) -> HTMLResponse:
    # Контекст для шаблона
    context = {"request": request, "user": user, "prediction": [], "errors": []}
    return templates.TemplateResponse("predict_iris.html", context)


@predict_iris_route.post("/predict_iris", response_class=HTMLResponse)
async def predict_iris(
    request: Request,
    sepal_length: float = Form(...),
    sepal_width: float = Form(...),
    petal_length: float = Form(...),
    petal_width: float = Form(...),
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user_via_cookies),
    rpc: RpcClient = Depends(get_rpc),
) -> HTMLResponse:
    errors = []
    flower_name = None

    try:
        prediction = await predict_processing(
            data=PredictionCreate(
                model="chatgpt-o4",
                input_data=[[sepal_length, sepal_width, petal_length, petal_width]],
            ),
            session=db,
            user={"id": user.id, "email": user.email},
            rpc=rpc,
        )
        print(f" BUILD_RESPONSE = {prediction}")
        result = prediction.result[0]

        if result in iris_map:
            flower_name = iris_map[result]
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Prediction mapping not found",
            )

    except HTTPException as e:
        errors.append(e.detail)
    except Exception as e:
        errors.append(str(e))

    # Контекст для шаблона
    context = {
        "request": request,
        "user": user,
        "prediction": flower_name,
        "errors": errors,
    }

    return templates.TemplateResponse("predict_iris.html", context)
