from typing import List, Optional

from sqlmodel import Session
from src.models.user import User
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="UserCRUD")


def get_all_users(session: Session) -> List[User]:
    """
    Получить всех пользователей из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для получения пользователей.

    Возвращает:
        Список всех объектов User, найденных в базе данных.
    """
    logger.info("Запрошен список всех пользователей")
    users = session.query(User).all()
    logger.debug(f"Найдено {len(users)} пользователей")
    return users


def get_user_by_id(id: int, session: Session) -> Optional[User]:
    """
    Получить пользователя из базы данных по его уникальному идентификатору.

    Аргументы:
        id: Уникальный идентификатор пользователя, которого нужно получить.
        session: Сессия базы данных, используемая для получения пользователя.

    Возвращает:
        Объект User, соответствующий предоставленному id, или None, если пользователь не найден.
    """
    logger.info(f"Запрошен пользователь по id={id}")
    user = session.get(User, id)
    if user:
        logger.debug(f"Пользователь с id={id} найден")
        return user
    logger.warning(f"Пользователь с id={id} не найден")
    return None


def get_user_by_email(email: str, session: Session) -> Optional[User]:
    """
    Получить пользователя из базы данных по его адресу электронной почты.

    Аргументы:
        email: Адрес электронной почты пользователя, которого нужно получить.
        session: Сессия базы данных, используемая для получения пользователя.

    Возвращает:
        Объект User, соответствующий предоставленному адресу электронной почты,
        или None, если пользователь не найден.
    """
    logger.info(f"Запрошен пользователь по email={email}")
    user = session.query(User).filter(User.email == email).first()  # type: ignore[arg-type]
    if user:
        logger.debug(f"Пользователь с email={email} найден")
        return user
    logger.warning(f"Пользователь с email={email} не найден")
    return None


def get_user_by_name(name: str, session: Session) -> Optional[User]:
    """
    Получить пользователя из базы данных по его имени.

    Аргументы:
        name: Имя пользователя, которого нужно получить.
        session: Сессия базы данных, используемая для получения пользователя.

    Возвращает:
        Объект User, соответствующий предоставленному имени,
        или None, если пользователь не найден.
    """
    logger.info(f"Запрошен пользователь по name={name}")
    user = session.query(User).filter(User.name == name).first()  # type: ignore[arg-type]
    if user:
        logger.debug(f"Пользователь с name={name} найден")
        return user
    logger.warning(f"Пользователь с name={name} не найден")
    return None


def create_user(new_user: User, session: Session) -> User | None:
    """
    Добавить нового пользователя в базу данных и зафиксировать транзакцию.

    Аргументы:
        new_user: Объект User, представляющий нового пользователя, которого нужно добавить.
        session: Сессия базы данных, используемая для добавления нового пользователя.

    Возвращает:
        Новый объект User с обновленным состоянием из базы данных, или None, если операция не удалась.
    """
    logger.info("Создается новый пользователь")
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    logger.info(f"Пользователь успешно создан (id={new_user.id})")
    return new_user


def update_user(user: User, session: Session) -> User | None:
    """
     Обновить пользователя в базу данных и зафиксировать транзакцию.

    Аргументы:
        user: Объект User, представляющий обновленного пользователя, которого нужно обновить.
        session: Сессия базы данных, используемая для добавления нового пользователя.

    Возвращает:
        объект User с обновленным состоянием из базы данных, или None, если операция не удалась.
    """
    logger.info(f"Обновление пользователя c id={user.id}")
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info(f"Пользователь с id={user.id} успешно обновлен")
    return user


def delete_user_by_id(id: int, session: Session) -> User:
    """
    Удалить пользователя из базы данных по его уникальному идентификатору.

    Аргументы:
        id: Уникальный идентификатор пользователя, которого нужно удалить.
        session: Сессия базы данных, используемая для удаления пользователя.

    Возвращает:
        Объект User, который был удален.

    Вызывает:
        Exception: Если пользователь с предоставленным id не найден.
    """
    logger.info(f"Попытка удалить пользователя с id={id}")
    user = session.get(User, id)
    if not user:
        logger.error(f"Пользователь с id={id} не найден для удаления")
        raise Exception("User not found")
    session.delete(user)
    session.commit()
    logger.info(f"Пользователь с id={id} успешно удален")
    return user


def delete_all_users(session: Session) -> None:
    """
    Удалить всех пользователей из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для удаления всех пользователей.

    Возвращает:
        None
    """
    logger.warning("Инициировано удаление всех пользователей")
    count = session.query(User).delete()
    session.commit()
    logger.info(f"Удалено {count} пользователей")
