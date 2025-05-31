from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.model import Model
from common.test_router_common import (
    client_fixture,
    session_fixture,
    secret_key_fixture,
    create_test_user_fixture,
    test_token_fixture,
    username_fixture,
    password_fixture,
    email_fixture,
)


def test_retrieve_all_models(client: TestClient, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/model/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_create_model(client: TestClient, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    new_model_data = {"name": "Test Model"}
    response = client.post("/api/model/new", json=new_model_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["name"] == new_model_data["name"]


def test_retrieve_model(client: TestClient, session: Session, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    new_model = Model(name="Demo Model")
    session.add(new_model)
    session.commit()
    response = client.get(f"/api/model/{new_model.id}", headers=headers)
    assert response.status_code == 200
    model_data = response.json()
    assert model_data["id"] == new_model.id
    assert model_data["name"] == new_model.name


def test_delete_model(client: TestClient, session: Session, test_token: str) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    new_model = Model(name="Temporary Model")
    session.add(new_model)
    session.commit()
    response = client.delete(f"/api/model/{new_model.id}", headers=headers)
    assert response.status_code == 200
    assert session.get(Model, new_model.id) is None


def test_delete_all_models(
    client: TestClient, session: Session, test_token: str
) -> None:
    headers = {"Authorization": f"Bearer {test_token}"}
    session.add(Model(name="Model One"))
    session.add(Model(name="Model Two"))
    session.commit()
    response = client.delete("/api/model/", headers=headers)
    assert response.status_code == 200
    assert session.query(Model).count() == 0
