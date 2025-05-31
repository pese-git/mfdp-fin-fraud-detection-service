import json
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from src.models.prediction import Prediction
from src.database.database import get_session
from src.auth.authenticate import get_current_user_via_cookies
from src.schemas import PredictionData, PredictInputData, User

# Словарь для отображения числовых предсказаний в текстовые названия
iris_map = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}


def format_flowar_type(value: int):
    try:
        return iris_map[value]
    except Exception as e:
        return e


predictions_route = APIRouter()
# Jinja2 templates
template_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=template_dir)


@predictions_route.get("/predictions", response_class=HTMLResponse)
async def read_predictions(
    request: Request,
    db: Session = Depends(get_session),
    user: User = Depends(get_current_user_via_cookies),
):
    # Извлечь историю предсказаний пользователя
    predictions = db.query(Prediction).filter(Prediction.user_id == user.id).all()

    predictions_data = []
    # Добавьте расчет списанных кредитов для предсказания, если необходимо
    for prediction in predictions:
        input_data_list = json.loads(prediction.input_data)
        input_data_res = []
        for input_data in input_data_list:
            input_data_res.append(
                PredictInputData(
                    sepal_length=input_data[0],
                    sepal_width=input_data[1],
                    petal_length=input_data[2],
                    petal_width=input_data[3],
                )
            )

        result_list = json.loads(prediction.result)
        result_res = []
        for result in result_list:
            result_res.append(format_flowar_type(result))

        predictions_data.append(
            PredictionData(
                id=prediction.id,
                input_data=input_data_res,
                result=result_res,
                credits_deducted=prediction.task.transaction.amount,
                created_at=prediction.created_at,
            )
        )
    #    prediction.credits_deducted = calculate_credits(prediction)

    # Создание контекста для шаблона
    context = {
        "request": request,
        "user": user,
        "predictions": predictions_data,
    }
    return templates.TemplateResponse("predictions.html", context)


def calculate_credits(prediction: Prediction) -> int:
    # Здесь должна быть логика для определения количества списанных кредитов
    return 0  # Или другая бизнес-логика для расчета
