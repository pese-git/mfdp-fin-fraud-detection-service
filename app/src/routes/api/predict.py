import logging
from datetime import datetime
import json
import time
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4
from src.services.logging.logging import get_logger
from src.models.fin_transaction import FinTransaction
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from sqlalchemy import Null, null
from sqlmodel import Session

from src.models.model import Model
#from src.services.rpc.rpc_client import RpcClient
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.task import Task
from src.services.rm.rm import RabbitMQClient, rabbit_client

logging.getLogger('pika').setLevel(logging.INFO)

logger = get_logger(logger_name=__name__)

#def get_rpc() -> RpcClient:
#    return RpcClient()


class PredictionCreate(BaseModel):
    """
    Модель данных для создания запроса предсказания.

    Атрибуты:
    - model (str): Название модели, которая будет использована для предсказания.
    - input_data (str): Входные данные, необходимые для выполнения предсказания.
    """

    isFraud: Optional[bool] = None
    TransactionID: int
    TransactionDT: int
    TransactionAmt: float
    ProductCD: str
    card1: Optional[int] = None
    card2: Optional[int] = None
    card3: Optional[float] = None
    card4: Optional[str] = None
    card5: Optional[float] = None
    card6: Optional[str] = None
    addr1: Optional[float] = None
    addr2: Optional[float] = None
    dist1: Optional[float] = None
    dist2: Optional[float] = None
    P_emaildomain: Optional[str] = None
    R_emaildomain: Optional[str] = None

    C: List[Optional[float]] = Field(..., min_items=14, max_items=14)
    D: List[Optional[Union[float, str]]] = Field(..., min_items=15, max_items=15)
    M: List[Optional[str]] = Field(..., min_items=9, max_items=9)
    V: List[Optional[float]] = Field(..., min_items=339, max_items=339)
    id: List[Optional[Union[str, float]]] = Field(..., min_items=27, max_items=27)

    class Config:
        #from_attributes = True
        schema_extra = {
            "example": {
                "TransactionID": 2987000,
                "TransactionDT": 86400,
                "TransactionAmt": 68.5,
                "ProductCD": "W",
                "card1": 13926,
                "card2": None,
                "card3": 150.0,
                "card4": "discover",
                "card5": 142.0,
                "card6": "credit",
                "addr1": 315.0,
                "addr2": 87.0,
                "dist1": 19.0,
                "dist2": None,
                "P_emaildomain": None,
                "R_emaildomain": None,
                "C": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 1.0, 1.0],
                "D": [14.0, None, 13.0, None, None, None, None, None, 13.0, 13.0, None, None, 0.0, 0.0, 0.0],
                "M": ["T", "M2", "F", "T", None, None, None, None, None],
                "V": [1.0 for _ in range(339)],
                "id": [None for _ in range(27)]
            }
        }


class PredictionResponse(BaseModel):
    """
    Модель данных для ответа с предсказанием.

    Атрибуты:
    - id (int): Уникальный идентификатор записи предсказания.
    - input_data (str): Данные, которые были использованы для генерации предсказания.
    - result (str): Результат или исход процесса предсказания.
    - created_at (datetime): Временная метка, указывающая, когда предсказание было создано.
    """

    id: int
    TransactionID: int
    TransactionDT: int
    TransactionAmt: float
    ProductCD: str
    card1: Optional[int] = None
    card2: Optional[int] = None
    card3: Optional[float] = None
    card4: Optional[str] = None
    card5: Optional[float] = None
    card6: Optional[str] = None
    addr1: Optional[float] = None
    addr2: Optional[float] = None
    dist1: Optional[float] = None
    dist2: Optional[float] = None
    P_emaildomain: Optional[str] = None
    R_emaildomain: Optional[str] = None
    isFraud: Optional[bool] = None

    C: List[Optional[float]] = Field(..., min_items=14, max_items=14)
    D: List[Optional[Union[float, str]]] = Field(..., min_items=15, max_items=15)
    M: List[Optional[str]] = Field(..., min_items=9, max_items=9)
    V: List[Optional[float]] = Field(..., min_items=339, max_items=339)
    ids: List[Optional[Union[str, float]]] = Field(..., min_items=27, max_items=27)

    created_at: datetime



#def make_rpc_call(rpc: RpcClient) -> Any:
#    def callback(input_data: dict[str, Any]) -> str:
#        print(f" [x] Запрос на вычисление ({input_data})")
#        result: str = rpc.call(input_data)
#        print(f" [.] Получен ответ: {result}")
#        return result
#
#    return callback


predict_router = APIRouter(tags=["Model Predict"])


# запрос на предсказание
@predict_router.post(
    "/",
    response_model=List[PredictionResponse],
    description="Создать новое предсказание на основе введенных данных и выбранной модели.",
)
async def predict(
    data: List[PredictionCreate] = Body(
        ...,
        example= [{
                "TransactionID": 2987000,
                "TransactionDT": 86400,
                "TransactionAmt": 68.5,
                "ProductCD": "W",
                "card1": 13926,
                "card2": None,
                "card3": 150.0,
                "card4": "discover",
                "card5": 142.0,
                "card6": "credit",
                "addr1": 315.0,
                "addr2": 87.0,
                "dist1": 19.0,
                "dist2": None,
                "P_emaildomain": None,
                "R_emaildomain": None,
                "C": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 1.0, 1.0],
                "D": [14.0, None, 13.0, None, None, None, None, None, 13.0, 13.0, None, None, 0.0, 0, 0],
                "M": ["T", "M2", "F", "T", None, None, None, None, None],
                "V": [1.0 for _ in range(339)],
                "id": [None for _ in range(27)]
            }],
    ),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
    #rpc: RabbitMQClient = Depends(rabbit_client),
) -> List[PredictionResponse]:

    # 1. Создать задачу и вернуть task_id
    task_response = await create_task(data, rabbit_client, session, user)
    task_id = task_response.task_id  # Здесь используем конкретное значение task_id

    start_wait_time = time.time()
    timeout = 60  # тайм-аут в секундах для задачи

    # 2. Ждать завершения задачи, проверяя её статус
    while True:
        status_response = await get_task_status(task_id, session, user)
        print(status_response)

        if status_response.status == "completed":
            break
        elif status_response.status == "failed":
            raise HTTPException(status_code=500, detail="Task processing failed")

        if time.time() - start_wait_time > timeout:
            raise HTTPException(status_code=408, detail="Task processing timed out")

        time.sleep(2)  # Ждем 2 секунды перед повторной проверкой статуса

    # 3. Получение и возврат результата
    result_response = await get_task_result(task_id, session, user)

    # Формирование окончательного ответа пользователю
    return result_response.predictions


class TaskResponse(BaseModel):
    task_id: str
    # status: str
    result: Optional[PredictionResponse] = None


@predict_router.post(
    "/task/create",
    response_model=TaskResponse,
    description="Создать новую задачу предсказания и вернуть её идентификатор.",
)
async def create_task(
    data: List[PredictionCreate] = Body(
        ...,
        example= [{
                "TransactionID": 2987000,
                "TransactionDT": 86400,
                "TransactionAmt": 68.5,
                "ProductCD": "W",
                "card1": 13926,
                "card2": None,
                "card3": 150.0,
                "card4": "discover",
                "card5": 142.0,
                "card6": "credit",
                "addr1": 315.0,
                "addr2": 87.0,
                "dist1": 19.0,
                "dist2": None,
                "P_emaildomain": None,
                "R_emaildomain": None,
                "C": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 1.0, 1.0],
                "D": [14.0, None, 13.0, None, None, None, None, None, 13.0, 13.0, None, None, 0.0, 0, 0],
                "M": ["T", "M2", "F", "T", None, None, None, None, None],
                "V": [1.0 for _ in range(339)],
                "id": [None for _ in range(27)]
            }],
    ),
    #rpc: RabbitMQClient = Depends(rabbit_client),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> TaskResponse:

    try:
        model = session.query(Model).first()
        if not model:
            raise HTTPException(status_code=400, detail="Model not found")
        
        # ГЕНЕРИРУЕМ task_id
        task_id = str(uuid4())
        # Подготавливаем MLTask (или свою структуру для RabbitMQ)
        mltask = {
            "task_id": task_id,
            "input_data": [pc.dict() for pc in data],
        }

        # Посылаем задачу через RabbitMQClient
        rabbit_client.send_task(mltask)
        
        # Сохраняем новую задачу в БД
        task = Task(
            task_id=task_id, status="init", model=model
        )
        session.add(task)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    return TaskResponse(task_id=task_id)


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict[str, Any]] = None


@predict_router.get("/task/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> TaskStatusResponse:

    task = session.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(task_id=task.task_id, status=task.status, result=None)


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    predictions: Optional[List[PredictionResponse]] = None




def as_list(value, default_len=None):

    if value is None:
        return [None] * default_len if default_len else []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            # Пробуем JSON-десериализацию
            val = json.loads(value)
            return val if isinstance(val, list) else [val]
        except Exception:
            return [value]  # Возможно, строка с одним значением
    # Если вдруг это число
    return [value]

def fin_transaction_to_prediction_response(obj: FinTransaction) -> PredictionResponse:
    # Преобразуйте объект FinTransaction к PredictionResponse  
    # (Поля должны полностью совпадать между этими моделями)
    return PredictionResponse(
        id=obj.id,
        TransactionID=obj.TransactionID,
        TransactionDT=obj.TransactionDT,
        TransactionAmt=obj.TransactionAmt,
        ProductCD=obj.ProductCD,
        card1=obj.card1,
        card2=obj.card2,
        card3=obj.card3,
        card4=obj.card4,
        card5=obj.card5,
        card6=obj.card6,
        addr1=obj.addr1,
        addr2=obj.addr2,
        dist1=obj.dist1,
        dist2=obj.dist2,
        P_emaildomain=obj.P_emaildomain,
        R_emaildomain=obj.R_emaildomain,
        isFraud=obj.isFraud,
        C=as_list(obj.C, default_len=14),   # Гарантируем список из 14 элементов
        D=as_list(obj.D, default_len=15),   # ...
        M=as_list(obj.M, default_len=9),
        V=as_list(obj.V, default_len=339),
        ids=as_list(getattr(obj, "ids", None), default_len=27),  # если поле называется ids в БД
        created_at=obj.created_at,
    )

@predict_router.get("/task/result/{task_id}", response_model=TaskResultResponse)
async def get_task_result(
    task_id: str,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> TaskResultResponse:

    task = session.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == "completed":
        transactions = task.fintransaction
        predictions = [fin_transaction_to_prediction_response(tx) for tx in transactions]
        return TaskResultResponse(
            task_id=task.task_id,
            status=task.status,
            predictions=predictions,
        )
    elif task.status == "failed":
        raise HTTPException(status_code=500, detail="Task processing failed")
    else:
        return TaskResultResponse(task_id=task.task_id, status=task.status)
    



@predict_router.post("/send_task_result", response_model=Dict[str, str])
async def send_task_result(
    task_id: str,
    data: List[PredictionCreate] = Body(
        ...,
        example= [{
                "TransactionID": 2987000,
                "TransactionDT": 86400,
                "TransactionAmt": 68.5,
                "ProductCD": "W",
                "card1": 13926,
                "card2": None,
                "card3": 150.0,
                "card4": "discover",
                "card5": 142.0,
                "card6": "credit",
                "addr1": 315.0,
                "addr2": 87.0,
                "dist1": 19.0,
                "dist2": None,
                "P_emaildomain": None,
                "R_emaildomain": None,
                "C": [1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 1.0, 1.0],
                "D": [14.0, None, 13.0, None, None, None, None, None, 13.0, 13.0, None, None, 0.0, 0, 0],
                "M": ["T", "M2", "F", "T", None, None, None, None, None],
                "V": [1.0 for _ in range(339)],
                "id": [None for _ in range(27)]
            }],
    ),
    session: Session = Depends(get_session),
    #mltask_service: MLTaskService = Depends(get_mltask_service)
) -> Dict[str, str]:
    """
    Endpoint for sending ML task using Result.
    Args:
        message (str): The message to be sent.
        user_id (int): ID of the user creating the task.
    Returns:
        Dict[str, str]: Response message with original and processed text.
    """
    try:
        task = session.query(Task).filter(Task.task_id == task_id).first()
        if not task:
            raise HTTPException(status_code=400, detail="Task not found")
        
        for pred in data:
            pred_data = pred.dict()
            if "id" in pred_data:
                pred_data["IDs"] = pred_data.pop("id")
            # task_id из Task связывается с FinTransaction
            pred_data["task_id"] = task.id
            fin = FinTransaction(**pred_data)
            session.add(fin)

        task.status="success"

        session.commit()
        logger.info(f"!!!!!!!!Task result has been set: {data}")
        return {"message": "Task result sent successfully!"}
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in sending task result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")