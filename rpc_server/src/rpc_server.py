import json
from typing import Any
import pika
from sqlalchemy import Engine
from src.database.config import get_settings
from .rpc_model import Model as MLModel
from sqlmodel import Session

from src.models.task import Task
from src.models.model import Model
from src.models.prediction import Prediction
from src.models.transaction import Transaction
from src.models.user import User
from src.models.wallet import Wallet

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
                    # Выполняем предсказание
                    result = self.model.predict(input_data)
                    # result = {"task_id": task_id, "prediction": prediction}

                    # Сохраняем предсказание в БД
                    prediction = Prediction(
                        user_id=task.transaction.user_id,
                        input_data=json.dumps(input_data),
                        result=json.dumps(result),
                    )
                    session.add(prediction)
                    session.flush()  # Применяем изменения в БД, но не фиксируем
                    session.refresh(prediction)  # Обновляем объект из БД

                    task.status = "completed"
                    task.prediction = prediction

                    session.add(task)
                    # session.flush()  # Применяем изменения в БД, но не фиксируем
                    # session.refresh(task)  # Обновляем объект из БД
                    session.commit()
                except Exception:
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
