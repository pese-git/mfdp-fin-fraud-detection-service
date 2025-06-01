from typing import Any
from unittest import mock
import pandas as pd
import mlflow
import pickle
import os
from dotenv import load_dotenv
import numpy as np
import torch

from sklearn.pipeline import Pipeline
from src.fraud_data_preprocessor import FraudDataPreprocessor  # ВАЖНО: этот импорт должен быть до joblib.load!
from torch_geometric.loader import DataLoader
from pathlib import Path

import joblib

load_dotenv()

#aws_key_id = os.getenv("AWS_ACCESS_KEY_ID")
#aws_key_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
#s3_endpoint_url = os.getenv("MLFLOW_S3_ENDPOINT_URL")

os.environ['MLFLOW_TRACKING_URI']= os.getenv('MLFLOW_URL')

#os.environ["AWS_ACCESS_KEY_ID"] = aws_key_id
#os.environ["AWS_SECRET_ACCESS_KEY"] = aws_key_secret
#os.environ["MLFLOW_S3_ENDPOINT_URL"] = s3_endpoint_url
import requests

def get_jwt_token(url: str, client_id: str, client_secret: str, username: str, password: str) -> str | None:
    """
    Получает JWT токен с использованием grant_type=password.
    
    :param url: URL для отправки POST-запроса
    :param client_id: ID клиента OAuth2
    :param client_secret: Секрет клиента OAuth2
    :param username: Имя пользователя
    :param password: Пароль пользователя
    :return: JWT токен (access_token) или None в случае ошибки
    """
    data = {
        "grant_type": "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password,
        "scope": "openid"
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # выбросит исключение при ошибке HTTP

        token = response.json().get("access_token")
        if token:
            print(f"JWT Token: {token}")
            return token
        else:
            print("Token not found in response.")
            return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
    except ValueError as json_err:
        print(f"Error decoding JSON: {json_err}")

    return None


def create_token():
    client_id = os.getenv("OAUTH_CLIENT_ID")
    client_secret = os.getenv("OAUTH_CLIENT_SECRET")
    oauth_endpoint_url = os.getenv("OAUTH_URL")
    username = os.getenv("MLFLOW_USERNAME")
    password = os.getenv("MLFLOW_PASSWORD")

    return get_jwt_token(
        url=oauth_endpoint_url,
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password

    )


class Model:
    """
    Класс для представления модели машинного обучения, использующей RandomForestClassifier
    из библиотеки scikit-learn. Этот класс автоматически создает и обучает
    модель с использованием датасета Iris при создании экземпляра.

    Методы
    -------
    _create_and_train_model() -> RandomForestClassifier
        Статический метод, который загружает датасет Iris, делит его на обучающую и
        тестовую выборки, обучает RandomForestClassifier на обучающей выборке
        и возвращает обученную модель.

    predict(input_data: Any) -> Any
        Метод предсказания, который принимает входные данные и возвращает предсказанные
        метки в виде списка.
    """

    def __init__(self) -> None:
        file_path = Path.cwd() / 'rpc_server' / 'preprocessor' / 'fraud_pipeline.joblib'
        self.pipeline = joblib.load(file_path)
        #self.pipeline = joblib.load('./rpc_server/preprocessor/fraud_pipeline.joblib')


        os.environ['MLFLOW_TRACKING_TOKEN'] = create_token()
        mlflow.set_experiment("antifraud_experiment")
        #logged_model = 'runs:/f885b232095c4c589c582a3ebfb3bed0/model'
        logged_model = 'runs:/615587bb4786452e8fc4b9b8cdb69adf/model'
        self.model = mlflow.pyfunc.load_model(logged_model)
        # Загрузить
        #№with open('./rpc_server/preprocessor/fraud_preprocessor.pkl', 'rb') as f:
        #    self.preprocessor = pickle.load(f)


    def predict(self, input_data: pd.DataFrame) -> Any:
        """
        Выполняет предсказания с использованием обученной модели RandomForestClassifier.

        Параметры
        ----------
        input_data : Any
            Входные данные, для которых нужно сделать предсказания.
            Это должно быть в формате, который ожидает модель, например,
            двумерный массив или DataFrame значений признаков.

        Возвращает
        -------
        Any
            Предсказанные метки для входных данных в виде списка.
        """
        # Приводим вход к DataFrame, если это возможно (ожидает shape: [n_samples, n_features])
 
        print(f"#### START PREDICT: {input_data}")
        base_test = self.pipeline.transform(input_data)
        print(f"#### PROCESSING DATA: {base_test}")


        input_df = base_test.astype({
            "card1_count": "float64",  # и другие поля, если нужно
        })
        input_df["TransactionDT"] = input_df["TransactionDT"].astype("int32")
        input_df["TransactionID"] = input_df["TransactionID"].astype("int32")
        pred = self.model.predict(input_df)
        # Для совместимости всегда возвращаем list, если возможно
        return pred
    