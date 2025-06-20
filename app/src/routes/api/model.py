from typing import Any, List, cast

import src.services.crud.model as ModelService
from fastapi import APIRouter, Body, Depends, HTTPException
from schemas import UserRead
from sqlmodel import Session
from src.auth.authenticate import authenticate
from src.database.database import get_session
from src.models.model import Model
from src.services.logging.logging import get_logger

model_router = APIRouter(tags=["Models"])


logger = get_logger(logger_name="api.model")


@model_router.get("/", response_model=List[Model])
async def retrieve_all_models(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> List[Model]:
    logger.info(
        "Пользователь '%s' (id=%s) запрашивает все модели",
        user.get("name"),
        user.get("id"),
    )
    models = ModelService.get_all_models(session=session)
    logger.debug("Получено моделей: %d", len(models) if models else 0)
    return cast(List[Model], models)


@model_router.get("/{model_id}", response_model=Model)
async def retrieve_model(
    model_id: int,
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Model:
    logger.info(
        "Пользователь '%s' (id=%s) запрашивает модель id=%s",
        user.get("name"),
        user.get("id"),
        model_id,
    )
    model = ModelService.get_model_by_id(model_id, session=session)
    if model is None:
        logger.warning("Модель id=%s не найдена", id)

        raise HTTPException(status_code=404, detail=f"Model with id={id} not found")
    logger.debug("Модель id=%s найдена", id)
    return model


@model_router.post("/new")
async def create_model(
    body: Model = Body(...),
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> Model:
    logger.info(
        "Пользователь '%s' (id=%s) создает модель: %r",
        user.get("name"),
        user.get("id"),
        body,
    )
    new_model = ModelService.create_model(body, session=session)
    logger.info("Создана новая модель с id=%s", getattr(new_model, "id", None))
    return new_model


@model_router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    session: Session = Depends(get_session),
    user: UserRead = Depends(authenticate),
) -> Model:
    try:
        logger.info(
            "Пользователь '%s' (id=%s) удаляет модель id=%s",
            user.name,
            user.id,
            model_id,
        )
        model = ModelService.delete_model_by_id(model_id, session=session)
        if model is None:
            logger.warning("Модель id=%s для удаления не найдена", model_id)
        else:
            logger.info("Удалена модель id=%s", model_id)
        return model
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail="Нельзя удалить модели: на них еще есть ссылки в задачах. Сначала удалите связанные задачи.",
        ) from e


@model_router.delete("/")
async def delete_all_models(
    session: Session = Depends(get_session),
    user: dict[str, Any] = Depends(authenticate),
) -> dict[str, Any]:
    try:
        ModelService.delete_all_models(session=session)
        logger.info("Все модели успешно удалены.")
        return {"message": "Models deleted successfully"}
    except Exception as e:
        logger.error("Ошибка при удалении моделей: %s", e)
        raise HTTPException(
            status_code=400,
            detail="Ошибка при удалении моделей. Возможно, существуют связанные задачи.",
        ) from e
