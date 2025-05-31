from fastapi import APIRouter, Body, Depends
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.model import Model
import src.services.crud.model as ModelService
from typing import Any, List, cast

model_router = APIRouter(tags=["Models"])


@model_router.get("/", response_model=List[Model])
async def retrieve_all_models(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[Model]:
    """
    Получить все модели из базы данных.

    Этот эндпоинт извлекает все записи моделей из базы данных
    и возвращает их в виде списка. Зависимость session предоставляет
    необходимую сессию базы данных для выполнения запросов.

    Параметры:
    - session: Сессия базы данных, автоматически предоставляемая
               механизмом Depends(get_session).

    Возвращает:
    - Список всех экземпляров моделей, присутствующих в базе данных.
    """
    return cast(List[Model], ModelService.get_all_models(session=session))


@model_router.get("/{id}", response_model=Model)
async def retrieve_model(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Model:
    """
    Получить конкретную модель по её ID.

    Этот эндпоинт извлекает одну запись модели из базы данных
    с использованием предоставленного ID модели. Зависимость session
    используется для взаимодействия с базой данных.

    Параметры:
    - id: Уникальный идентификатор модели, которую нужно получить.
    - session: Сессия базы данных, автоматически предоставляемая
               механизмом Depends(get_session).

    Возвращает:
    - Экземпляр модели, соответствующий указанному ID.

    Исключения:
    - HTTPException: Если модель с указанным ID не найдена,
      возвращается ошибка HTTP 404.
    """
    return ModelService.get_model_by_id(id, session=session)


@model_router.post("/new")
async def create_model(
    body: Model = Body(...),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Model:
    """
    Создать новый экземпляр модели в базе данных.

    Этот эндпоинт получает экземпляр модели в теле запроса
    и создает новую запись в базе данных. Зависимость session
    облегчает взаимодействие с базой данных для создания модели.

    Параметры:
    - body: Данные модели, предоставленные в теле запроса,
            используемые для создания нового экземпляра модели.
    - session: Сессия базы данных, автоматически предоставляемая
               механизмом Depends(get_session).

    Возвращает:
    - Новый созданный экземпляр модели.
    """
    new_model = ModelService.create_model(body, session=session)
    return new_model


@model_router.delete("/{id}")
async def delete_model(
    id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Model:
    """
    Удалить конкретную модель по её ID.

    Этот эндпоинт обеспечивает удаление записи модели из базы данных
    с использованием её уникального идентификатора. Зависимость session
    используется для выполнения необходимых операций в базе данных для удаления.

    Параметры:
    - id: Уникальный идентификатор модели, которую нужно удалить.
    - session: Сессия базы данных, автоматически предоставляемая
               механизмом Depends(get_session).

    Возвращает:
    - Экземпляр модели, который был удалён из базы данных.

    Исключения:
    - HTTPException: Если модель с указанным ID не найдена,
      возвращается ошибка HTTP 404.
    """
    return ModelService.delete_model_by_id(id, session=session)


@model_router.delete("/")
async def delete_all_models(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> dict[str, Any]:
    """
    Удалить все экземпляры моделей из базы данных.

    Этот эндпоинт удаляет все записи моделей из базы данных.
    Параметр session используется для выполнения операции удаления
    в базе данных. После удаления изменения фиксируются
    для сохранения удаления.

    Параметры:
    - session: Сессия базы данных, используемая для выполнения
               операции удаления и фиксации изменений.

    Возвращает:
    - None: Эта функция не возвращает никаких значений.
    """
    ModelService.delete_all_models(session=session)
    return {"message": "Models deleted successfully"}
