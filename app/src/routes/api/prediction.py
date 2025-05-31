from fastapi import APIRouter, Body, status, Depends
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.prediction import Prediction
import src.services.crud.prediction as PredictionService
from typing import Any, List, cast

prediction_router = APIRouter(tags=["Prediciton"])


@prediction_router.get("/", response_model=List[Prediction])
async def retrieve_all_predictions(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[Prediction]:
    """
    Получить список всех записей предсказаний из базы данных.

    Этот эндпоинт извлекает все предсказания, хранящиеся в базе данных,
    используя метод `get_all_predictions` из сервиса PredictionService.
    Он зависит от сессии базы данных, предоставленной зависимостью `get_session`.

    Возвращает:
        List[Prediction]: Список объектов Prediction, представляющих все
        записи предсказаний в базе данных.
    """
    return cast(
        List[Prediction], PredictionService.get_all_predictions(session=session)
    )


@prediction_router.get("/{id}", response_model=Prediction)
async def retrieve_predict(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Prediction:
    """
    Получить конкретную запись предсказания по её ID из базы данных.

    Этот эндпоинт получает одно предсказание на основе заданного ID, используя
    метод `get_prediction_by_id` из сервиса PredictionService. Он требует наличия
    сессии базы данных, предоставленной зависимостью `get_session`.

    Аргументы:
        id (int): Уникальный идентификатор предсказания для получения.
        session: Зависимость от сессии базы данных для взаимодействия с базой данных.

    Возвращает:
        Prediction: Объект Prediction, соответствующий указанному ID.

    Исключения:
        HTTPException: Если предсказание с заданным ID не существует, вызывается
        исключение.
    """
    return PredictionService.get_prediction_by_id(id, session=session)


@prediction_router.post(
    "/new", response_model=Prediction, status_code=status.HTTP_201_CREATED
)
async def create_prediction(
    body: Prediction = Body(...),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Prediction:
    """
    Создать новую запись предсказания в базе данных.

    Этот эндпоинт позволяет клиентам создать новую запись предсказания,
    предоставив необходимые данные в теле запроса. Метод `create_prediction`
    из сервиса PredictionService используется для сохранения нового предсказания
    в базе данных. Функция зависит от сессии базы данных, предоставленной
    зависимостью `get_session`.

    Аргументы:
        body (Prediction): Данные предсказания для создания, предоставленные в теле запроса.
        session: Зависимость от сессии базы данных для взаимодействия с базой данных.

    Возвращает:
        dict: Словарь, содержащий детали вновь созданного предсказания.
    """
    new_prediction = PredictionService.create_prediction(body, session=session)
    return new_prediction


@prediction_router.delete("/{id}", response_model=Prediction)
async def delete_prediction(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Prediction:
    """
    Удалить конкретную запись предсказания по её ID из базы данных.

    Этот эндпоинт удаляет одно предсказание из базы данных, используя метод
    `delete_predict_by_id` из сервиса PredictionService. Он требует уникальный
    идентификатор предсказания для удаления, а также сессию базы данных,
    предоставленную зависимостью `get_session`.

    Аргументы:
        id (int): Уникальный идентификатор предсказания для удаления.
        session: Зависимость от сессии базы данных для взаимодействия с базой данных.

    Возвращает:
        dict: Словарь, подтверждающий успешное удаление предсказания.

    Исключения:
        HTTPException: Если предсказание с заданным ID не существует, вызывается
        исключение.
    """
    return PredictionService.delete_predict_by_id(id, session=session)


@prediction_router.delete("/")
async def delete_all_predictions(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> dict[str, Any]:
    """
    Удалить все записи предсказаний из базы данных.

    Этот эндпоинт удаляет все записи предсказаний в базе данных, используя метод
    `delete_all_predicts` из сервиса PredictionService. Он зависит от сессии базы
    данных, предоставленной зависимостью `get_session`.

    Аргументы:
        session: Зависимость от сессии базы данных для взаимодействия с базой данных.

    Возвращает:
        dict: Словарь, подтверждающий успешное удаление всех предсказаний.
    """
    PredictionService.delete_all_predicts(session=session)
    return {"message": "Предсказания удалены успешно"}
