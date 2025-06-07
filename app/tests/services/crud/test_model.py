from sqlmodel import Session
from src.models.model import Model
from src.services.crud.model import (
    create_model,
    delete_all_models,
    delete_model_by_id,
    get_all_models,
    get_model_by_id,
)
from tests.common.test_router_common import *  # [wildcard-import]


def test_create_model(session: Session) -> None:
    new_model = Model(name="Test Model", path="/path/to/model")
    created_model = create_model(new_model, session)
    assert created_model is not None
    assert created_model.id is not None
    assert created_model.name == "Test Model"


def test_get_all_models(session: Session) -> None:
    models = [
        Model(name="Model One", path="/path/to/model1"),
        Model(name="Model Two", path="/path/to/model2"),
    ]
    session.add_all(models)
    session.commit()

    retrieved_models = get_all_models(session)
    assert len(retrieved_models) == 2
    assert all(isinstance(m, Model) for m in retrieved_models)


def test_get_model_by_id(session: Session) -> None:
    model = Model(name="Unique Model", path="/unique/path")
    session.add(model)
    session.commit()

    retrieved_model = get_model_by_id(model.id, session)
    assert retrieved_model is not None
    assert retrieved_model.id == model.id


def test_delete_model_by_id(session: Session) -> None:
    model = Model(name="Delete Test", path="/delete/path")
    session.add(model)
    session.commit()

    deleted_model = delete_model_by_id(model.id, session)
    assert deleted_model.id == model.id
    assert get_model_by_id(model.id, session) is None


def test_delete_all_models(session: Session) -> None:
    session.add_all(
        [
            Model(name="Model One", path="/path/to/one"),
            Model(name="Model Two", path="/path/to/two"),
        ]
    )
    session.commit()

    delete_all_models(session)
    assert len(get_all_models(session)) == 0
