from sqlmodel import Session 
from models.user import User

def test_create_user(session: Session):
    try:
        user = User(id=0, email="test_2@mail.ru", password="123")
        session.add(user)
        session.commit()
        assert True
    except:
        assert False
        
def test_delete_user(session: Session):
    try:
        user = session.get(User, 0)
        if user:
            session.delete(user)
            session.commit()
            assert True
        else:
            assert False
    except Exception as ex:
        assert False, ex
        

