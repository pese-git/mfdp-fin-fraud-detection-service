from database.config import get_settings
from database.database import get_session, init_db, engine
from services.crud.user import get_all_users, create_user
from sqlmodel import Session
from models.event import Event
from models.user import User


if __name__ == "__main__":
    test_user = User(email='test@mail.ru', password='test')
    test_user_2 = User(email='test@mail.ru', password='test')
    test_user_3 = User(email='test@mail.ru', password='test')
    
    
    # settings = get_settings()
    # print(settings.DB_HOST)
    # print(settings.DB_NAME)
    
    init_db()
    print('Init db has been success')
    
    with Session(engine) as session:
        create_user(test_user, session)
        create_user(test_user_2, session)
        create_user(test_user_3, session)
        users = get_all_users(session)

    for user in users:
        print(f'id: {user.id} - {user.email}')
