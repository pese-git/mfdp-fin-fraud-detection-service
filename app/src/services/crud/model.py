from sqlmodel import Session
from src.models.model import Model
from typing import List, Optional
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="ModelCRUD")


def get_all_models(session: Session) -> List[Model]:
    """
    Получить все экземпляры модели из базы данных.

    :param session: Сессия базы данных, используемая для выполнения запроса.
    :return: Список, содержащий все экземпляры Model, найденные в базе данных.
    """
    logger.info("Запрошен список всех моделей")
    models = session.query(Model).all()
    logger.debug(f"Найдено {len(models)} моделей")
    return models


def get_model_by_id(id: int, session: Session) -> Optional[Model]:
    """
    Получить экземпляр модели из базы данных по ее ID.

    :param id: Уникальный идентификатор модели, которую нужно получить.
    :param session: Сессия базы данных, используемая для выполнения запроса.
    :return: Экземпляр Model с указанным ID, или None, если не найден.
    """
    model = session.get(Model, id)
    if model:
        logger.debug(f"Модель с id={id} найдена")
        return model
    logger.warning(f"Модель с id={id} не найдена")
    return None


def create_model(new_model: Model, session: Session) -> Model:
    """
    Добавить новый экземпляр модели в базу данных и зафиксировать транзакцию.

    :param new_model: Экземпляр Model, который будет добавлен в базу данных.
    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: Экземпляр Model, который был добавлен в базу данных, с обновленным состоянием.
    """
    logger.info("Создается новая модель")
    session.add(new_model)
    session.commit()
    session.refresh(new_model)
    logger.info(f"Модель успешно создана (id={new_model.id})")
    return new_model


def delete_model_by_id(id: int, session: Session) -> Model:
    """
    Удалить экземпляр модели из базы данных по ее ID.

    :param id: Уникальный идентификатор модели, которую нужно удалить.
    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: Экземпляр Model, который был удален.
    :raises Exception: Если Model с указанным ID не найдена.
    """
    logger.info(f"Попытка удалить модель с id={id}")
    model = session.get(Model, id)
    if not model:
        logger.error(f"Модель с id={id} не найдена для удаления")
        raise Exception("User not found")
    session.delete(model)
    session.commit()
    logger.info(f"Модель с id={id} успешно удалена")
    return model


def delete_all_models(session: Session) -> None:
    """
    Удалить все экземпляры модели из базы данных.

    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: None
    """
    logger.warning("Инициировано удаление всех моделей")
    count = session.query(Model).delete()
    session.commit()
    logger.info(f"Удалено {count} моделей")
