import logging
from typing import Any, Dict, List, Union

import pandas as pd
from rmq.schemas import PredictionCreate
from rpc_model import Model

# Логгер для всей библиотеки
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# === Константы структуры данных ===
BASE_FIELDS = [
    "TransactionID",
    "TransactionDT",
    "TransactionAmt",
    "ProductCD",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "addr1",
    "addr2",
    "dist1",
    "dist2",
    "P_emaildomain",
    "R_emaildomain",
]
ARRAY_SPECS = {
    "C": 14,
    "D": 15,
    "M": 9,
    "V": 339,
    "id": 27,
}
ISFRAUD_FIELD = "isFraud"


def convert_dataframe_to_predictions(df: pd.DataFrame) -> List[PredictionCreate]:
    """
    Преобразует DataFrame в список PredictionCreate, учитывая ВСЕ массивные поля
    """
    predictions = []
    for _, row in df.iterrows():
        record = {}

        # Базовые поля
        for field in BASE_FIELDS:
            record[field] = row.get(field)

        # Массивы
        for array_name, length in ARRAY_SPECS.items():
            if array_name == "id":
                # Совместимость со старыми датасетами с id1, ..., id27
                record["id"] = [row.get(f"id{i+1}") for i in range(length)] if "id1" in row else [None] * length
            else:
                record[array_name] = [row.get(f"{array_name}{i+1}") for i in range(length)]

        # Доп. поле isFraud (если есть)
        if ISFRAUD_FIELD in row:
            record[ISFRAUD_FIELD] = row.get(ISFRAUD_FIELD)

        # Валидация Pydantic
        predictions.append(PredictionCreate(**record))
    return predictions


def convert_json_to_dataframe(data: Any) -> pd.DataFrame:
    """
    Преобразует список dict (или один dict) с транзакцией в DataFrame.
    Массивные поля конвертируются в плоские столбцы (C1..C14, id1..id27, и т.д.)
    """

    def unpack_row(row: Any) -> dict:
        flat = {field: row[field] for field in BASE_FIELDS}
        for array_name, length in ARRAY_SPECS.items():
            data_array = row.get(array_name, [])
            for i in range(length):
                key = f"id{i+1}" if array_name == "IDs" else f"{array_name}{i+1}"
                flat[key] = data_array[i] if i < len(data_array) else None
        return flat

    rows = data if isinstance(data, list) else [data]
    unpacked = [unpack_row(r) for r in rows]
    return pd.DataFrame(unpacked)


class AntifraudModelHandler:
    """Обёртка для антифрод модели (инициализация, инференс, сериализация)."""

    def __init__(self) -> None:
        self.model = Model()

    def predict_with_metadata(self, input_json: Any) -> List[PredictionCreate]:
        """
        Принимает JSON, выполняет предикт, объединяет вход с результатом, возвращает PredictionCreate.
        """
        data = input_json["input_data"]
        df = convert_json_to_dataframe(data)
        logger.info("Antifraud model input DataFrame shape: %s", df.shape)
        prediction_result = self.model.predict(df)
        df_result = df.copy()
        df_result[ISFRAUD_FIELD] = prediction_result[ISFRAUD_FIELD].to_numpy()
        return convert_dataframe_to_predictions(df_result)


# ========== Интерфейсы (singletons) ==========

_antifraud_handler_singleton = None


def get_antifraud_handler() -> AntifraudModelHandler:
    global _antifraud_handler_singleton
    if _antifraud_handler_singleton is None:
        _antifraud_handler_singleton = AntifraudModelHandler()
    return _antifraud_handler_singleton


def run_antifraud_task(input_json: Any) -> List[PredictionCreate]:
    """Точка входа для вычисления задачи антифрода. Принимает JSON, возвращает PredictionCreate."""
    handler = get_antifraud_handler()
    return handler.predict_with_metadata(input_json)
