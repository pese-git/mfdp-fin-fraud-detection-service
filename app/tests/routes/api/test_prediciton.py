import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session
from fastapi import status

from src.models.prediction import Prediction
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


def test_retrieve_all_predictions(client: TestClient, session: Session, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/api/prediction/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_create_prediction(client: TestClient, session: Session, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    new_prediction_data = {
        "input_data": "sample input",
        "result": "sample result",
        "user_id": test_user.id,
    }
    response = client.post(
        "/api/prediction/new", json=new_prediction_data, headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["input_data"] == new_prediction_data["input_data"]
    assert response_data["result"] == new_prediction_data["result"]


def test_retrieve_prediction(
    client: TestClient, session: Session, test_user, test_token
):
    headers = {"Authorization": f"Bearer {test_token}"}
    new_prediction = Prediction(
        input_data="test input", result="test result", user_id=test_user.id
    )
    session.add(new_prediction)
    session.commit()
    response = client.get(f"/api/prediction/{new_prediction.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    prediction_data = response.json()
    assert prediction_data["input_data"] == new_prediction.input_data
    assert prediction_data["result"] == new_prediction.result


def test_delete_prediction(client: TestClient, session: Session, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    new_prediction = Prediction(
        input_data="delete input", result="delete result", user_id=test_user.id
    )
    session.add(new_prediction)
    session.commit()
    response = client.delete(f"/api/prediction/{new_prediction.id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert session.get(Prediction, new_prediction.id) is None


def test_delete_all_predictions(
    client: TestClient, session: Session, test_user, test_token
):
    headers = {"Authorization": f"Bearer {test_token}"}
    session.add(Prediction(input_data="input1", result="result1", user_id=test_user.id))
    session.add(Prediction(input_data="input2", result="result2", user_id=test_user.id))
    session.commit()
    response = client.delete("/api/prediction/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert session.query(Prediction).count() == 0
