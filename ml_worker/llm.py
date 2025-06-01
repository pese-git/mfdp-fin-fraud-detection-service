import logging
from typing import Any, Dict, List, Union
import pandas as pd

from rpc_model import Model

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _parse_response(response_text: str) -> str:
    """Парсит ответ (заглушка для обратной совместимости)

    Оставлен для обратной совместимости. Типы входных/выходных данных могут быть изменены в будущем.
    """
    return response_text


def _transaction_df_to_json(df: pd.DataFrame) -> list:
    """
    Преобразует DataFrame обратно в list[dict] с вложенными массивами C, D, M, V, id
    (структура подходит для PredictionCreate).
    """
    records = []
    for _, row in df.iterrows():
        record = {}

        # Базовые поля
        base_fields = [
            "TransactionID", "TransactionDT", "TransactionAmt", "ProductCD",
            "card1", "card2", "card3", "card4", "card5", "card6",
            "addr1", "addr2", "dist1", "dist2", "P_emaildomain", "R_emaildomain",
        ]
        for key in base_fields:
            record[key] = row.get(key)

        # Массивы
        record["C"] = [row.get(f"C{i+1}") for i in range(14)]
        record["D"] = [row.get(f"D{i+1}") for i in range(15)]
        record["M"] = [row.get(f"M{i+1}") for i in range(9)]
        record["V"] = [row.get(f"V{i+1}") for i in range(339)]
        record["id"] = [row.get(f"id{i+1}") for i in range(27)] if "id1" in row else [None for _ in range(27)]

        # Добавить isFraud если он есть
        if "isFraud" in row:
            record["isFraud"] = row.get("isFraud")
        records.append(record)

    return records

def _transaction_json_to_df(data):
        # Если на вход пришел список — обработать все элементы
        if isinstance(data, list):
            out_list = []
            for row in data:
                out = {}
                base_fields = [
                    "TransactionID","TransactionDT","TransactionAmt","ProductCD",
                    "card1","card2","card3","card4","card5","card6",
                    "addr1","addr2","dist1","dist2","P_emaildomain","R_emaildomain"
                ]
                for key in base_fields:
                    out[key] = row[key]

                for i in range(14):
                    out[f"C{i+1}"] = row["C"][i] if i < len(row["C"]) else None

                for i in range(15):
                    out[f"D{i+1}"] = row["D"][i] if i < len(row["D"]) else None

                for i in range(9):
                    out[f"M{i+1}"] = row["M"][i] if i < len(row["M"]) else None

                for i in range(339):
                    out[f"V{i+1}"] = row["V"][i] if i < len(row["V"]) else None

                # for i in range(27):
                #     out[f"id{i+1}"] = row["id"][i] if i < len(row["id"]) else None

                out_list.append(out)
            df = pd.DataFrame(out_list)
        else:
            # исходная логика для одиночного словаря
            out = {}
            base_fields = [
                "TransactionID","TransactionDT","TransactionAmt","ProductCD",
                "card1","card2","card3","card4","card5","card6",
                "addr1","addr2","dist1","dist2","P_emaildomain","R_emaildomain"
            ]
            for key in base_fields:
                out[key] = data[key]

            for i in range(14):
                out[f"C{i+1}"] = data["C"][i] if i < len(data["C"]) else None

            for i in range(15):
                out[f"D{i+1}"] = data["D"][i] if i < len(data["D"]) else None

            for i in range(9):
                out[f"M{i+1}"] = data["M"][i] if i < len(data["M"]) else None

            for i in range(339):
                out[f"V{i+1}"] = data["V"][i] if i < len(data["V"]) else None

            # for i in range(27):
            #     out[f"id{i+1}"] = data["id"][i] if i < len(data["id"]) else None

            df = pd.DataFrame([out])
        return df
    
def __transaction_json_to_df(data: Union[Dict, List[Dict]]) -> pd.DataFrame:
    """
    Преобразует dict или список dict транзакций к DataFrame (логика из rpc_server.py).
    """
    base_fields = [
        "TransactionID", "TransactionDT", "TransactionAmt", "ProductCD",
        "card1", "card2", "card3", "card4", "card5", "card6",
        "addr1", "addr2", "dist1", "dist2", "P_emaildomain", "R_emaildomain"
    ]
    def row_to_dict(row):
        out = {key: row.get(key) for key in base_fields}
        out.update({f"C{i+1}": row["C"][i] if "C" in row and i < len(row.get("C", [])) else None for i in range(14)})
        out.update({f"D{i+1}": row["D"][i] if "D" in row and i < len(row.get("D", [])) else None for i in range(15)})
        out.update({f"M{i+1}": row["M"][i] if "M" in row and i < len(row.get("M", [])) else None for i in range(9)})
        out.update({f"V{i+1}": row["V"][i] if "V" in row and i < len(row.get("V", [])) else None for i in range(339)})
        return out

    if isinstance(data, list):
        return pd.DataFrame([row_to_dict(row) for row in data])
    else:
        return pd.DataFrame([row_to_dict(data)])

class AntifraudPredictor:
    """Обёртка для anti-fraud ML модели (инициализация и предикт)."""
    def __init__(self):
        self.model = Model()

    def predict(self, input_json: Union[Dict, List[Dict]]) -> Any:
        #df = _transaction_json_to_df(input_json['input_data'])
        #logger.info("Antifraud: DataFrame shape %s", df.shape)
        #result = self.model.predict(df)

        # Выполняем предсказание
        df = _transaction_json_to_df(input_json['input_data'])
        logger.info("Antifraud: DataFrame shape %s", df.shape)
        result = self.model.predict(df)
        # Объединяем входные данные с предсказанием (чтобы в каждой строке был isFraud)
        df_with_pred = df.copy()
        df_with_pred["isFraud"] = result["isFraud"].to_numpy()
        return _transaction_df_to_json(df_with_pred)

# Singleton, чтобы модель не грузилась каждый раз
_antifraud_predictor = None

def antifraud_predict(input_json: Union[Dict, List[Dict]]) -> Any:
    """
    Предикт для антифрода.
    Аргумент: input_json — dict (или list[dict]) с полями транзакции
    Возвращает результат предсказания модели (тип может меняться: массив, list и т.п.)
    """
    global _antifraud_predictor
    if _antifraud_predictor is None:
        _antifraud_predictor = AntifraudPredictor()
    return _antifraud_predictor.predict(input_json)

def do_task(input_json: Any) -> Any:
    """
    Выполняет задачу предсказания антифрода.
    Args:
        input_json: dict или list[dict] с данными транзакций

    Returns:
        Результат predict модели (тип данных может меняться)
    """
    return antifraud_predict(input_json)