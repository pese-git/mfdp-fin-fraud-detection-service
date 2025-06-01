#import pytest
#from sqlmodel import SQLModel, Session, create_engine
#from sqlalchemy.pool import StaticPool
##from src.models.prediction import Prediction
#from src.services.crud.prediction import (
#    get_all_predictions,
#    get_prediction_by_id,
#    create_prediction,
#    delete_predict_by_id,
#    delete_all_predicts,
#)
#
#from common.test_router_common import session_fixture
#
#
#def test_create_prediction(session: Session) -> None:
#    new_prediction = Prediction(
#        input_data="Input data", result="Result data", user_id=1
#    )
#    created_prediction = create_prediction(new_prediction, session)
#    assert created_prediction is not None
#    assert created_prediction.id is not None
#    assert created_prediction.input_data == "Input data"
#
#
#def test_get_all_predictions(session: Session) -> None:
#    predictions = [
#        Prediction(input_data="Input 1", result="Result 1", user_id=1),
#        Prediction(input_data="Input 2", result="Result 2", user_id=1),
#    ]
#    session.add_all(predictions)
#    session.commit()
#
#    retrieved_predictions = get_all_predictions(session)
#    assert len(retrieved_predictions) == 2
#    assert all(isinstance(p, Prediction) for p in retrieved_predictions)
#
#
#def test_get_prediction_by_id(session: Session) -> None:
#    prediction = Prediction(
#        input_data="Unique Input", result="Unique Result", user_id=1
#    )
#    session.add(prediction)
#    session.commit()
#
#    retrieved_prediction = get_prediction_by_id(prediction.id, session)
#    assert retrieved_prediction is not None
#    assert retrieved_prediction.id == prediction.id
#
#
#def test_delete_predict_by_id(session: Session) -> None:
#    prediction = Prediction(
#        input_data="Delete Input", result="Delete Result", user_id=1
#    )
#    session.add(prediction)
#    session.commit()
#
#    deleted_prediction = delete_predict_by_id(prediction.id, session)
#    assert deleted_prediction.id == prediction.id
#    assert get_prediction_by_id(prediction.id, session) is None
#
#
#def test_delete_all_predicts(session: Session) -> None:
#    session.add_all(
#        [
#            Prediction(input_data="Delete Input1", result="Delete Result1", user_id=1),
#            Prediction(input_data="Delete Input2", result="Delete Result2", user_id=1),
#        ]
#    )
#    session.commit()
#
#    delete_all_predicts(session)
#    assert len(get_all_predictions(session)) == 0
