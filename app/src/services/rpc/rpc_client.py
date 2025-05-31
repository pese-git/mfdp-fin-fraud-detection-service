import json
from typing import Any
import pika
import uuid
from src.database.config import get_settings


class RpcClient:
    """
    Класс для реализации клиента RPC (удаленного вызова процедур) на основе RabbitMQ, который обрабатывает
    асинхронное взаимодействие с сервером RabbitMQ для выполнения удаленных вызовов процедур.

    Атрибуты:
        connection (pika.BlockingConnection): Соединение с сервером RabbitMQ.
        channel (pika.adapters.blocking_connection.BlockingChannel): Канал для взаимодействия с сервером RabbitMQ.
        callback_queue (str): Имя очереди для обратного вызова.
        response (str): Ответ, полученный от сервера.
        corr_id (str): Идентификатор корреляции для сопоставления запросов и ответов.

    Методы:
        on_response(ch, method, properties, body):
            Функция обратного вызова, выполняемая при получении сообщения. Проверяет,
            соответствует ли идентификатор корреляции, и устанавливает атрибут ответа.

        call(n):
            Публикует сообщение в очередь RabbitMQ, ожидает ответа и
            возвращает ответ в виде JSON-объекта.
    """

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

    def call(self, input_data: dict[str, Any]) -> str:
        """
        Ставим задачу в очередь и возвращаем ID задачи.

        Параметры:
            input_data: Данные, используемые для выполнения предсказания.

        Возвращает:
            task_id: Уникальный идентификатор задачи.
        """
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
        """
        Функция обратного вызова для обработки ответов от сервера RabbitMQ.

        Этот метод вызывается, когда сообщение получено в очереди обратного вызова.
        Он проверяет, совпадает ли идентификатор корреляции входящего сообщения с
        тем, который был отправлен с запросом. Если они совпадают, ответ
        сохраняется в атрибуте response экземпляра.

        Параметры:
            ch: Объект канала.
            method: Информация о методе доставки.
            properties: Свойства полученного сообщения, включающие
                        идентификатор корреляции, который используется для сопоставления ответов с запросами.
            body: Тело сообщения, которое содержит данные ответа.
        """
        if self.corr_id == properties.correlation_id:
            self.response = body


# import json
# import pika
# import uuid
# from src.database.config import get_settings
#
# class RpcClient:
#    """
#    Класс для реализации клиента RPC (удаленного вызова процедур) на основе RabbitMQ, который обрабатывает
#    асинхронное взаимодействие с сервером RabbitMQ для выполнения удаленных вызовов процедур.
#
#    Атрибуты:
#        connection (pika.BlockingConnection): Соединение с сервером RabbitMQ.
#        channel (pika.adapters.blocking_connection.BlockingChannel): Канал для взаимодействия с сервером RabbitMQ.
#        callback_queue (str): Имя очереди для обратного вызова.
#        response (str): Ответ, полученный от сервера.
#        corr_id (str): Идентификатор корреляции для сопоставления запросов и ответов.
#
#    Методы:
#        on_response(ch, method, properties, body):
#            Функция обратного вызова, выполняемая при получении сообщения. Проверяет,
#            соответствует ли идентификатор корреляции, и устанавливает атрибут ответа.
#
#        call(n):
#            Публикует сообщение в очередь RabbitMQ, ожидает ответа и
#            возвращает ответ в виде JSON-объекта.
#    """
#    def __init__(self):
#        # Параметры подключения
#        connection_params = pika.ConnectionParameters(
#            host=get_settings().RABBITMQ_HOST,  # Замените на адрес вашего RabbitMQ сервера
#            port=5672,          # Порт по умолчанию для RabbitMQ
#            virtual_host='/',   # Виртуальный хост (обычно '/')
#            credentials=pika.PlainCredentials(
#                username=get_settings().RABBITMQ_DEFAULT_USER,  # Имя пользователя по умолчанию
#                password=get_settings().RABBITMQ_DEFAULT_PASS  # Пароль по умолчанию
#            ),
#            heartbeat=60,
#            blocked_connection_timeout=2
#        )
#        self.connection = pika.BlockingConnection(connection_params)
#        self.channel = self.connection.channel()
#
#        result = self.channel.queue_declare(queue='', exclusive=True)
#        self.callback_queue = result.method.queue
#
#        self.channel.basic_consume(
#            queue=self.callback_queue,
#            on_message_callback=self.on_response,
#            auto_ack=True
#        )
#
#    def on_response(self, ch, method, properties, body):
#        """
#        Функция обратного вызова для обработки ответов от сервера RabbitMQ.
#
#        Этот метод вызывается, когда сообщение получено в очереди обратного вызова.
#        Он проверяет, совпадает ли идентификатор корреляции входящего сообщения с
#        тем, который был отправлен с запросом. Если они совпадают, ответ
#        сохраняется в атрибуте response экземпляра.
#
#        Параметры:
#            ch: Объект канала.
#            method: Информация о методе доставки.
#            properties: Свойства полученного сообщения, включающие
#                        идентификатор корреляции, который используется для сопоставления ответов с запросами.
#            body: Тело сообщения, которое содержит данные ответа.
#        """
#        if self.corr_id == properties.correlation_id:
#            self.response = body
#
#    def call(self, n):
#        """
#        Отправляет удаленный вызов процедуры на сервер RabbitMQ и ждет ответа.
#
#        Этот метод публикует сообщение в назначенную очередь RabbitMQ с уникальным
#        идентификатором корреляции и синхронно ждет, пока ответ не будет получен. Как только
#        ответ получен, он возвращается в виде JSON-объекта.
#
#        Параметры:
#            n: Полезная нагрузка сообщения, отправляемая в запросе, обычно числовое значение.
#
#        Возвращает:
#            dict: Ответ от сервера RabbitMQ, обработанный в виде JSON-объекта.
#
#        Процесс:
#            - Инициализирует атрибут response значением None.
#            - Генерирует уникальный идентификатор корреляции для запроса.
#            - Публикует сообщение в очередь RabbitMQ с идентификатором корреляции и
#              очередью ответа, установленной для асинхронного ответа.
#            - Обрабатывает события в соединении, пока ответ не будет установлен.
#            - Возвращает ответ, как только он получен и обработан.
#        """
#        self.response = None
#        self.corr_id = str(uuid.uuid4())
#
#        self.channel.basic_publish(
#            exchange='',
#            routing_key=get_settings().RABBITMQ_QUEUE,
#            properties=pika.BasicProperties(
#                reply_to=self.callback_queue,
#                correlation_id=self.corr_id
#            ),
#            body=str(n)
#        )
#
#        while self.response is None:
#            self.connection.process_data_events()
#
#        return json.loads(self.response)
