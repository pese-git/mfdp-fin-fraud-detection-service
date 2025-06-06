import json
import pika
import logging
from typing import Optional

from .rmqconf import RabbitMQConfig
from src.services.logging.logging import get_logger

# Устанавливаем уровень логирования для pika через встроенный логгер
logging.getLogger('pika').setLevel(logging.INFO)

logger = get_logger(logger_name="RabbitMQClient")


class RabbitMQClient:
    """
    Клиент для взаимодействия с RabbitMQ.
    
    Attributes:
        connection_params: Параметры подключения к RabbitMQ серверу
        queue_name: Имя очереди для ML задач
    """
    
    def __init__(self, config: RabbitMQConfig):
        self.connection_params = config.get_connection_params()
        self.queue_name = config.queue_name

    def send_task(self, task: dict) -> bool:
        """
        Отправляет ML задачу в очередь RabbitMQ.
        """
        logger.info(f"Попытка отправить задачу в очередь '{self.queue_name}'")
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
            logger.debug("Соединение с RabbitMQ установлено")

            # Создаем очередь если её нет
            channel.queue_declare(queue=self.queue_name)
            logger.debug(f"Очередь '{self.queue_name}' создана или уже существует")

            # Подготавливаем сообщение
            message = json.dumps(task)
            logger.debug(f"Сообщение подготовлено для отправки: {message}")

            # Отправляем сообщение
            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message
            )
            logger.info(f"Сообщение успешно отправлено в очередь '{self.queue_name}'")
            connection.close()
            logger.debug("Соединение с RabbitMQ закрыто")
            return True

        except pika.exceptions.AMQPError as e:
            logger.error(f"Ошибка RabbitMQ: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Неизвестная ошибка при отправке задачи в RabbitMQ: {str(e)}", exc_info=True)
            return False

# Создаем глобальный экземпляр клиента
rabbitmq_config = RabbitMQConfig()
rabbit_client = RabbitMQClient(rabbitmq_config)