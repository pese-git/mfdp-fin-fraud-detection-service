from sqlmodel import Session
from src.models.model import Model
from typing import List, Optional


def get_all_models(session: Session) -> List[Model]:
    """
    Получить все экземпляры модели из базы данных.

    :param session: Сессия базы данных, используемая для выполнения запроса.
    :return: Список, содержащий все экземпляры Model, найденные в базе данных.
    """
    return session.query(Model).all()


def get_model_by_id(id: int, session: Session) -> Optional[Model]:
    """
    Получить экземпляр модели из базы данных по ее ID.

    :param id: Уникальный идентификатор модели, которую нужно получить.
    :param session: Сессия базы данных, используемая для выполнения запроса.
    :return: Экземпляр Model с указанным ID, или None, если не найден.
    """
    return session.get(Model, id)


def create_model(new_model: Model, session: Session) -> Model:
    """
    Добавить новый экземпляр модели в базу данных и зафиксировать транзакцию.

    :param new_model: Экземпляр Model, который будет добавлен в базу данных.
    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: Экземпляр Model, который был добавлен в базу данных, с обновленным состоянием.
    """
    session.add(new_model)
    session.commit()
    session.refresh(new_model)
    return new_model


def delete_model_by_id(id: int, session: Session) -> Model:
    """
    Удалить экземпляр модели из базы данных по ее ID.

    :param id: Уникальный идентификатор модели, которую нужно удалить.
    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: Экземпляр Model, который был удален.
    :raises Exception: Если Model с указанным ID не найдена.
    """
    model = session.get(Model, id)
    if not model:
        raise Exception("User not found")
    # Удаляем модель
    session.delete(model)
    session.commit()
    return model


def delete_all_models(session: Session) -> None:
    """
    Удалить все экземпляры модели из базы данных.

    :param session: Сессия базы данных, используемая для выполнения операции.
    :return: None
    """
    session.query(Model).delete()
    session.commit()
