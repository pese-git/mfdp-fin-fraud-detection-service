from datetime import datetime
import json
import time
from typing import Any, Callable, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlmodel import Session

from src.models.model import Model
from src.services.rpc.rpc_client import RpcClient
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.task import Task


def get_rpc() -> RpcClient:
    return RpcClient()


class PredictionCreate(BaseModel):
    """
    Модель данных для создания запроса предсказания.

    Атрибуты:
    - model (str): Название модели, которая будет использована для предсказания.
    - input_data (str): Входные данные, необходимые для выполнения предсказания.
    """

    model: str
    input_data: dict[str, Any] | list[Any]

    class Config:
        schema_extra = {
            "example": {
                "model": "chatgpt-o4",
                "input_data": [
                    [5.1, 3.5, 1.4, 0.2],
                    [6.7, 3.1, 4.7, 1.5],
                    [5.9, 3.0, 5.1, 1.8],
                    [6.3, 2.8, 5.6, 2.1],
                    [4.9, 3.0, 1.4, 0.2],
                ],
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
    input_data: dict[str, Any] | list[Any]
    result: dict[str, Any] | list[Any]
    created_at: datetime


def make_rpc_call(rpc: RpcClient) -> Any:
    def callback(input_data: dict[str, Any]) -> str:
        print(f" [x] Запрос на вычисление ({input_data})")
        result: str = rpc.call(input_data)
        print(f" [.] Получен ответ: {result}")
        return result

    return callback


predict_router = APIRouter(tags=["Model Predict"])


# запрос на предсказание
@predict_router.post(
    "/",
    response_model=PredictionResponse,
    description="Создать новое предсказание на основе введенных данных и выбранной модели.",
)
async def predict(
    data: PredictionCreate = Body(
        ...,
        example={
            "model": "chatgpt-o4",
            "input_data": [
                [5.1, 3.5, 1.4, 0.2],
                [6.7, 3.1, 4.7, 1.5],
                [5.9, 3.0, 5.1, 1.8],
                [6.3, 2.8, 5.6, 2.1],
                [4.9, 3.0, 1.4, 0.2],
            ],
        },
    ),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
    rpc: RpcClient = Depends(get_rpc),
) -> Optional[PredictionResponse]:
    """
    Создать запись предсказания для заданного пользователя и модели.

    Этот конечный точка принимает POST-запрос для генерации предсказания на основе
    введенных данных и модели, указанной пользователем. Он использует функцию
    predict_processing для обработки логики предсказания.

    Параметры:
    - user_id (int): ID пользователя, делающего запрос на предсказание.
    - data (PredictionCreate): Экземпляр, содержащий название модели и данные ввода,
      необходимые для предсказания.
    - session (Session, optional): Зависимость сессии базы данных для взаимодействия с
      базой данных, по умолчанию используется сессия, полученная от get_session.

    Возвращает:
    - PredictionResponse: Модель ответа, содержащая детали предсказания, такие как
      ID предсказания, входные данные, результат и временную метку, когда оно было создано.

    Примеры значений входных данных:
    - [5.1, 3.5, 1.4, 0.2] — Пример данных для Setosa.
    - [6.7, 3.1, 4.7, 1.5] — Пример данных для Versicolor.
    - [5.9, 3.0, 5.1, 1.8] — Пример данных для Virginica.
    - [6.3, 2.8, 5.6, 2.1] — Пример данных для Virginica.
    - [4.9, 3.0, 1.4, 0.2] — Пример данных для Setosa.
    """
    # 1. Создать задачу и вернуть task_id
    task_response = await create_task(data, rpc, session, user)
    task_id = task_response.task_id  # Здесь используем конкретное значение task_id

    start_wait_time = time.time()
    timeout = 30  # тайм-аут в секундах для задачи

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
    return result_response.prediction


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
    data: PredictionCreate = Body(
        ...,
        example={
            "model": "chatgpt-o4",
            "input_data": [
                [5.1, 3.5, 1.4, 0.2],
                [6.7, 3.1, 4.7, 1.5],
                [5.9, 3.0, 5.1, 1.8],
                [6.3, 2.8, 5.6, 2.1],
                [4.9, 3.0, 1.4, 0.2],
            ],
        },
    ),
    rpc: RpcClient = Depends(get_rpc),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> TaskResponse:
    """
    Создать новую задачу предсказания для введенных данных и модели.

    Эта функция создает задачу предсказания, списывает стоимость предсказания
    с кошелька пользователя и возвращает идентификатор созданной задачи.

    Параметры:
    - data (PredictionCreate): Объект, содержащий информацию о модели и входных данных для предсказания.
    - rpc (RpcClient, optional): Клиент RPC для постановки задачи в очередь.
    - session (Session, optional): Сессия базы данных для выполнения операций с базой данных.
    - user (dict, optional): Аутентифицированный пользователь, выполняющий запрос.

    Исключения:
    - HTTPException: Возникает, если модель не найдена в базе данных или если у пользователя
      недостаточно средств для совершения транзакции. Также возникает при ошибках сервера.

    Возвращает:
    - TaskResponse: Объект, содержащий идентификатор созданной задачи.
    """
    try:
        # with session.begin():  # Начинаем транзакцию
        # Получаем ML модель
        model = session.query(Model).filter(Model.name == data.model).first()
        if not model:
            raise HTTPException(status_code=400, detail="Model not found")
        
        # Генерация task_id и постановка задачи в очередь
        task_id = rpc.call(data.input_data)
        task = Task(
            task_id=task_id, status="init", model=model
        )
        session.add(task)
        session.commit()

    except Exception as e:
        session.rollback()  # Откатываем изменения в случае ошибки
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
    """
    Получить статус задачи по указанному task_id.

    Этот endpoint предназначен для получения текущего статуса задачи по ее уникальному идентификатору.
    Он запрашивает базу данных для поиска задачи с переданным идентификатором и возвращает статус задачи.

    Параметры:
    - task_id (str): Уникальный идентификатор задачи, статус которой необходимо получить.
    - session (Session, optional): Зависимость сессии базы данных для взаимодействия с базой данных.
    - user (dict, optional): Информация о текущем аутентифицированном пользователе, полученная через зависимость аутентификации.

    Возвращает:
    - TaskStatusResponse: Модель ответа, содержащая идентификатор задачи и ее текущий статус.

    Исключения:
    - HTTPException: Возникает, если задача с указанным идентификатором не найдена в базе данных, возвращая статус 404 (Task not found).
    """
    task = session.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(task_id=task.task_id, status=task.status, result=None)


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    prediction: Optional[PredictionResponse] = None


@predict_router.get("/task/result/{task_id}", response_model=TaskResultResponse)
async def get_task_result(
    task_id: str,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> TaskResultResponse:
    """
    Получить результат выполнения задачи по указанному task_id.

    Этот endpoint используется для получения результата выполнения задачи по ее уникальному идентификатору.
    Метод запрашивает базу данных, чтобы найти задачу с переданным идентификатором и вернуть результат
    предсказания, если задача завершена успешно.

    Параметры:
    - task_id (str): Уникальный идентификатор задачи, результат которой необходимо получить.
    - session (Session, optional): Зависимость сессии базы данных для взаимодействия с базой данных.
    - user (dict, optional): Информация о текущем аутентифицированном пользователе, полученная через зависимость аутентификации.

    Возвращает:
    - TaskResultResponse: Модель ответа, содержащая идентификатор задачи, статус задачи, и
      объект PredictionResponse с данными предсказания, если задача завершена успешно.

    Исключения:
    - HTTPException: Возникает, если задача с указанным идентификатором не найдена в базе данных, возвращая статус 404 (Task not found).
    - HTTPException: Возникает, если задача завершена с ошибкой, возращая статус 500 (Task processing failed).
    """
    task = session.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == "completed":
        return TaskResultResponse(
            task_id=task.task_id,
            status=task.status,
            prediction=PredictionResponse(
                id=task.prediction.id,
                input_data=json.loads(task.prediction.input_data),
                result=json.loads(task.prediction.result),
                created_at=task.prediction.created_at,
            ),
        )
    elif task.status == "failed":
        raise HTTPException(status_code=500, detail="Task processing failed")
    else:
        return TaskResultResponse(task_id=task.task_id, status=task.status)
