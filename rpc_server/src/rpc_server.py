import json
import traceback
import pandas as pd
from typing import Any
import pika
from sqlalchemy import Engine
from src.models.fin_transaction import FinTransaction
from src.database.config import get_settings
from .rpc_model import Model as MLModel
from sqlmodel import Session

from src.models.task import Task
from src.models.model import Model
#from src.models.prediction import Prediction
#from src.models.transaction import Transaction
from src.models.user import User
#from src.models.wallet import Wallet

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties


class RPCServer:

    def __init__(self, engine: Engine) -> None:
        self.model = MLModel()
        self.connection = self._create_connection()
        self.channel = self._create_channel()
        self.engine = engine

    @staticmethod
    def _create_connection() -> pika.BlockingConnection:
        """
        Устанавливает и возвращает блокирующее соединение с сервером RabbitMQ.

        Этот метод использует параметры соединения, полученные из настроек приложения,
        включая хост, порт, виртуальный хост и учетные данные для аутентификации.
        Кроме того, он задает интервал отправки сигнала «heartbeat» и таймаут
        для заблокированного соединения, чтобы обеспечить его стабильность и отзывчивость.

        Возвращает:
        --------
        pika.BlockingConnection
            Объект блокирующего соединения с сервером RabbitMQ.

        Исключения:
        -------
        pika.exceptions.AMQPConnectionError
            Если возникает ошибка при установлении соединения с сервером RabbitMQ.
        """
        connection_params = pika.ConnectionParameters(
            host=get_settings().RABBITMQ_HOST,
            port=5672,
            virtual_host="/",
            credentials=pika.PlainCredentials(
                username=get_settings().RABBITMQ_DEFAULT_USER,
                password=get_settings().RABBITMQ_DEFAULT_PASS,
            ),
            heartbeat=60,
            blocked_connection_timeout=2,
        )
        return pika.BlockingConnection(connection_params)

    def _create_channel(self) -> BlockingChannel:
        """
        Объявляет и возвращает канал, связанный с соединением RabbitMQ.

        Эта функция устанавливает слой связи для взаимодействия с
        брокером сообщений RabbitMQ. Она конкретно объявляет очередь с именем,
        полученным из настроек приложения. Эта очередь служит конечной точкой
        для приема и ответа на запросы RPC.

        Возвращает:
        --------
        pika.channel.Channel
            Объект канала для взаимодействия с указанной очередью RabbitMQ.

        Исключения:
        -------
        pika.exceptions.ChannelError
            Если возникает ошибка при установлении или объявлении канала.
        """
        channel = self.connection.channel()
        channel.queue_declare(queue=get_settings().RABBITMQ_QUEUE)
        return channel

    def on_request(
        self,
        ch: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> Any:
        task_info = json.loads(body)
        task_id = task_info["task_id"]
        input_data = task_info["input_data"]

        with Session(self.engine) as session:
            # Получаем Task
            task = session.query(Task).filter(Task.task_id == task_id).first()
            if task:
                try:
                    print(f'### INPUT DATA: {input_data}')
                    # Выполняем предсказание
                    df = self.transaction_json_to_df(input_data)
                    result = self.model.predict(df)

                    # Объединяем входные данные с предсказанием (чтобы в каждой строке был isFraud)
                    df_with_pred = df.copy()
                    df_with_pred["isFraud"] = result["isFraud"].to_numpy()

                    # Сохраняем все транзакции
                    fin_transactions = []
                    for _, row in df_with_pred.iterrows():
                        row_dict = row.to_dict()
                        row_dict["task_id"] = task.id  # или task.task_id - используйте корректное id
                        fin_transaction = FinTransaction(**row_dict)
                        session.add(fin_transaction)
                        fin_transactions.append(fin_transaction)

                    session.flush()  # чтобы получить id при необходимости

                    for ft in fin_transactions:
                        session.refresh(ft)
                    
                    # result = {"task_id": task_id, "prediction": prediction}

                    # Сохраняем предсказание в БД
                    #prediction = Prediction(
                    #    #user_id=task.transaction.user_id,
                    #    input_data=json.dumps(input_data),
                    ##    result=json.dumps(result),
                    ##)
                    ##session.add(prediction)
                    ##session.flush()  # Применяем изменения в БД, но не фиксируем
                    ##session.refresh(prediction)  # Обновляем объект из БД#

                    task.status = "completed"
                    #task.prediction = prediction

                    session.add(task)
                    # session.flush()  # Применяем изменения в БД, но не фиксируем
                    # session.refresh(task)  # Обновляем объект из БД
                    session.commit()
                except Exception as e:
                    print("Произошла ошибка:", e)
                    traceback.print_exc()
                    task.status = "failed"
                    session.add(task)
                    session.commit()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self) -> None:
        """
        Запускает RPC сервер для прослушивания запросов.

        Этот метод настраивает качество обслуживания для канала RabbitMQ, чтобы гарантировать,
        что только одно сообщение обрабатывается за раз (количество предварительных
        выборок равно 1). Затем начинает потребление сообщений из указанной очереди,
        используя метод `on_request` в качестве обратного вызова для обработки каждого
        входящего сообщения.

        Метод эффективно помещает сервер в цикл, в котором он ждет
        входящих RPC-запросов и обрабатывает их бесконечно до тех пор, пока соединение
        не будет закрыто или не возникнет ошибка.

        Он использует имя очереди, настроенное в настройках приложения, чтобы привязать
        потребителя и отображает сообщение, указывающее, что сервер готов принимать
        запросы.

        Возвращает:
        --------
        None
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=get_settings().RABBITMQ_QUEUE, on_message_callback=self.on_request
        )
        print(" [x] Ожидание RPC запросов")
        self.channel.start_consuming()



    def transaction_json_to_df(self, data):
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
