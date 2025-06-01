import json
from typing import Any
import pika
import uuid
from src.database.config import get_settings


class RpcClient:

    def __init__(self) -> None:
        # Параметры подключения
        connection_params = pika.ConnectionParameters(
            host=get_settings().RABBITMQ_HOST,  # Замените на адрес вашего RabbitMQ сервера
            port=5672,  # Порт по умолчанию для RabbitMQ
            virtual_host="/",  # Виртуальный хост (обычно '/')
            credentials=pika.PlainCredentials(
                username=get_settings().RABBITMQ_DEFAULT_USER,  # Имя пользователя по умолчанию
                password=get_settings().RABBITMQ_DEFAULT_PASS,  # Пароль по умолчанию
            ),
            heartbeat=60,
            blocked_connection_timeout=2,
        )
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

    def call(self, input_data: list[dict[str, Any]]) -> str:

        self.response = None
        self.corr_id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())  # Создаем уникальный идентификатор задачи

        self.channel.basic_publish(
            exchange="",
            routing_key=get_settings().RABBITMQ_QUEUE,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue, correlation_id=self.corr_id
            ),
            body=json.dumps({"task_id": task_id, "input_data": input_data}),
        )

        return task_id

    def on_response(self, ch: Any, method: Any, properties: Any, body: Any) -> None:

        if self.corr_id == properties.correlation_id:
            self.response = body

