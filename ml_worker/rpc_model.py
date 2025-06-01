from typing import Any
from unittest import mock
import pandas as pd
import mlflow
import pickle
import os
import numpy as np
import torch

from sklearn.pipeline import Pipeline
from src.fraud_data_preprocessor import FraudDataPreprocessor  # ВАЖНО: этот импорт должен быть до joblib.load!
from torch_geometric.loader import DataLoader
from pathlib import Path

import joblib
import requests

from rmq.rmqconf import ML_CONFIG  # Импорт централизованной конфигурации
import logging

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Можно выставить уровень логирования

# Настройка трекинга MLflow
os.environ['MLFLOW_TRACKING_URI'] = ML_CONFIG.mlflow_url

def get_jwt_token(url: str, client_id: str, client_secret: str, username: str, password: str) -> str | None:
    """
    Получает JWT токен с использованием grant_type=password.
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
            logger.info(f"JWT Token: {token}")
            return token
        else:
            logger.warning("Token not found in response.")
            return None

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - {response.text}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception occurred: {req_err}")
    except ValueError as json_err:
        logger.error(f"Error decoding JSON: {json_err}")

    return None


def create_token():
    return get_jwt_token(
        url=ML_CONFIG.oauth_url,
        client_id=ML_CONFIG.oauth_client_id,
        client_secret=ML_CONFIG.oauth_client_secret,
        username=ML_CONFIG.mlflow_username,
        password=ML_CONFIG.mlflow_password,
    )


class Model:
    """
    Класс для представления модели машинного обучения.
    """

    def __init__(self) -> None:
        from src.fraud_data_preprocessor import FraudDataPreprocessor  # ВАЖНО: этот импорт должен быть до joblib.load!
        
        file_path = Path.cwd() / ML_CONFIG.fraud_pipeline_path
        self.pipeline = joblib.load(file_path)
        os.environ['MLFLOW_TRACKING_TOKEN'] = create_token()
        mlflow.set_experiment(ML_CONFIG.mlflow_experiment)
        self.model = mlflow.pyfunc.load_model(ML_CONFIG.logged_model_uri)

    def predict(self, input_data: pd.DataFrame) -> Any:
        """
        Выполняет предсказания с использованием обученной модели RandomForestClassifier.
        """
        from src.fraud_data_preprocessor import FraudDataPreprocessor  # ВАЖНО: этот импорт должен быть до joblib.load!

        logger.info(f"#### START PREDICT: {input_data}")
        base_test = self.pipeline.transform(input_data)
        logger.info(f"#### PROCESSING DATA: {base_test}")

        input_df = base_test.astype({
            "card1_count": "float64",  # и другие поля, если нужно
        })
        input_df["TransactionDT"] = input_df["TransactionDT"].astype("int32")
        input_df["TransactionID"] = input_df["TransactionID"].astype("int32")
        pred = self.model.predict(input_df)
        return pred