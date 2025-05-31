from sqlmodel import Session
from src.models.user import User
from typing import List, Optional


def get_all_users(session: Session) -> List[User]:
    """
    Получить всех пользователей из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для получения пользователей.

    Возвращает:
        Список всех объектов User, найденных в базе данных.
    """
    return session.query(User).all()


def get_user_by_id(id: int, session: Session) -> Optional[User]:
    """
    Получить пользователя из базы данных по его уникальному идентификатору.

    Аргументы:
        id: Уникальный идентификатор пользователя, которого нужно получить.
        session: Сессия базы данных, используемая для получения пользователя.

    Возвращает:
        Объект User, соответствующий предоставленному id, или None, если пользователь не найден.
    """
    return session.get(User, id)


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
    return session.query(User).filter(User.email == email).first()


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
    return session.query(User).filter(User.name == name).first()


def create_user(new_user: User, session: Session) -> User | None:
    """
    Добавить нового пользователя в базу данных и зафиксировать транзакцию.

    Аргументы:
        new_user: Объект User, представляющий нового пользователя, которого нужно добавить.
        session: Сессия базы данных, используемая для добавления нового пользователя.

    Возвращает:
        Новый объект User с обновленным состоянием из базы данных, или None, если операция не удалась.
    """
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
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
    session.add(user)
    session.commit()
    session.refresh(user)
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
    user = session.get(User, id)
    if not user:
        raise Exception("User not found")
    # Удаляем пользователя
    session.delete(user)
    session.commit()
    return user


def delete_all_users(session: Session) -> None:
    """
    Удалить всех пользователей из базы данных.

    Аргументы:
        session: Сессия базы данных, используемая для удаления всех пользователей.

    Возвращает:
        None
    """
    session.query(User).delete()
    session.commit()
