from fastapi import APIRouter, Body, status, Depends
from sqlmodel import Session
from src.models.fin_transaction import FinTransaction
from src.auth.authenticate import authenticate
from src.database.database import get_session
#from src.models.prediction import Prediction
import src.services.crud.fin_transaction as FinTransactionService
from typing import Any, List, cast

fin_transaction_router = APIRouter(tags=["Transaction"])


@fin_transaction_router.get("/", response_model=List[FinTransaction])
async def retrieve_all_transactions(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[FinTransaction]:
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
        List[FinTransaction], FinTransactionService.get_all_fin_transaction(session=session)
    )


@fin_transaction_router.get("/{id}", response_model=FinTransaction)
async def retrieve_transaction(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> FinTransaction | None:
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
    return FinTransactionService.get_fin_transaction_by_id(id, session=session)


#@fin_transaction_router.post(
#    "/new", response_model=FinTransaction, status_code=status.HTTP_201_CREATED
#)
#async def create_transaction(
#    body: FinTransaction = Body(...),
#    session: Session = Depends(get_session),
#    user: dict[str, Any] = Depends(authenticate),
#) -> FinTransaction:
#    """
#    Создать новую запись предсказания в базе данных.
#
#    Этот эндпоинт позволяет клиентам создать новую запись предсказания,
#    предоставив необходимые данные в теле запроса. Метод `create_prediction`
#    из сервиса PredictionService используется для сохранения нового предсказания
#    в базе данных. Функция зависит от сессии базы данных, предоставленной
#    зависимостью `get_session`.
#
#    Аргументы:
#        body (Prediction): Данные предсказания для создания, предоставленные в теле запроса.
#        session: Зависимость от сессии базы данных для взаимодействия с базой данных.
#
#    Возвращает:
#        dict: Словарь, содержащий детали вновь созданного предсказания.
#    """
#    new_prediction = FinTransactionService.create_fin_transaction(body, session=session)
#    return new_prediction


@fin_transaction_router.delete("/{id}", response_model=FinTransaction)
async def delete_transaction(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> FinTransaction:
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
    return FinTransactionService.delete_fin_trnsaction_by_id(id, session=session)


@fin_transaction_router.delete("/")
async def delete_all_transactions(
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
    FinTransactionService.delete_all_fin_transactions(session=session)
    return {"message": "Предсказания удалены успешно"}
