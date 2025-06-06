#import pytest
#from sqlmodel import SQLModel, Session, create_engine, select
#from sqlalchemy.pool import StaticPool
#from src.models.wallet import Wallet
#from src.models.transaction import Transaction, TransactionType
#from src.services.crud.balance import get_balance_by_user_id, update_balance_by_user_id
#
#from common.test_router_common import session_fixture
#
#
#def test_get_balance_by_user_id(session: Session) -> None:
#    wallet = Wallet(user_id=1, balance=1000)
#    session.add(wallet)
#    session.commit()
#
#    balance = get_balance_by_user_id(user_id=1, session=session)
#    assert balance == 1000
#
#
#def test_get_balance_by_user_id_not_found(session: Session) -> None:
#    try:
#        balance = get_balance_by_user_id(user_id=999, session=session)
#        assert balance is None
#    except RuntimeError:
#        pass
#
#
#def test_update_balance_by_user_id(session: Session) -> None:
#    wallet = Wallet(user_id=1, balance=1000)
#    session.add(wallet)
#    session.commit()
#
#    response = update_balance_by_user_id(user_id=1, amount=500, session=session)
#    assert response == 1000 + 500
#
#    # Check if balance was updated
#    updated_balance = get_balance_by_user_id(user_id=1, session=session)
#    assert updated_balance == 1500
#
#    # Check if transaction was created
#    transactions = session.exec(
#        select(Transaction).where(Transaction.user_id == 1)
#    ).all()
#    assert len(transactions) == 1
#    assert transactions[0].amount == 500
#    assert transactions[0].transaction_type == TransactionType.INCOME
#
#
#def test_update_balance_by_user_id_wallet_not_found(session: Session) -> None:
#    with pytest.raises(Exception, match="Not found wallet"):
#        update_balance_by_user_id(user_id=999, amount=500, session=session)
