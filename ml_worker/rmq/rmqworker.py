import json
import logging
import time
from typing import Any

import pika
import requests
from antifraud_model_handler import run_antifraud_task
from rmq.rmqconf import APP_SERVICE_CONFIG, RabbitMQConfig
from rmq.schemas import PredictionCreate

# logging конфиг — универсальный стиль
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("pika").setLevel(logging.WARNING)


class RabbitMQLlmWorker:
    """
    Рабочий ML-класс для получения задач из RabbitMQ, их обработки и отправки результатов.
    """

    MAX_RETRIES = 3
    RETRY_DELAY_SEC = 0.5
    RESULT_ENDPOINT = APP_SERVICE_CONFIG.get_request_url()

    def __init__(self, config: RabbitMQConfig):
        self.config = config
        self.connection = None
        self.channel = None

    # ==== RabbitMQ setup and teardown ====
    def connect(self) -> None:
        """Установить соединение с RabbitMQ с повторными попытками."""
        while True:
            try:
                params: pika.ConnectionParameters = self.config.get_connection_params()
                self.connection = pika.BlockingConnection(params)
                if self.connection is None:
                    logger.error("BlockingConnection returned None! Check connection params.")
                    time.sleep(self.RETRY_DELAY_SEC)
                    continue
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.config.queue_name)
                logger.info("Connected to RabbitMQ")
                break
            except Exception as e:
                logger.error(f"RabbitMQ connect error: {e!r}")
                time.sleep(self.RETRY_DELAY_SEC)

    def close(self) -> None:
        """Корректно закрыть канал и соединение."""
        try:
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()
            logger.info("RabbitMQ connections closed")
        except Exception as exc:
            logger.error(f"Error closing RabbitMQ connection: {exc!r}")

    # ==== Результаты ====
    def send_task_result(self, task_id: str, result: list[PredictionCreate]) -> bool:
        """
        Отправить результат обработки задачи на указанный endpoint.
        Преобразует PredictionCreate к dict для сериализации.
        """
        try:
            json_payload = [pred.model_dump() for pred in result]
            response = requests.post(self.RESULT_ENDPOINT, params={"task_id": task_id}, json=json_payload)
            response.raise_for_status()
            logger.info(f"Result sent for task {task_id}")
            return True
        except Exception as exc:
            logger.error(f"Result send failed for task {task_id}: {exc!r}")
            return False

    # ==== Callback ====
    def process_message(self, ch: Any, method: Any, properties: Any, body: Any) -> None:
        """
        Обработка входящего сообщения из RabbitMQ.
        """
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                logger.info(f"Received message: {body!r}")
                msg = json.loads(body.decode("utf-8"))
                result = run_antifraud_task(msg)
                if self.send_task_result(msg["task_id"], result):
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info("Task acknowledgment sent")
                    return
                else:
                    raise RuntimeError("Task result send failed")
            except Exception as exc:
                retries += 1
                logger.error(f"Processing error (try {retries}): {exc!r}")
                if retries >= self.MAX_RETRIES:
                    logger.error("Max retries reached, message rejected")
                    ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
                    return
                time.sleep(self.RETRY_DELAY_SEC)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_worker(self) -> None:
        """Запуск обработки очереди (блокирующий вызов)."""
        if self.channel is None:
            logger.error("RabbitMQ channel is not established. Did you call connect()?")
            raise RuntimeError("No channel. Call connect() before start_worker().")
        try:
            self.channel.basic_consume(queue=self.config.queue_name, on_message_callback=self.process_message, auto_ack=False)
            logger.info("Worker started. Press Ctrl+C to stop.")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Shutting down by user CTRL+C.")
        finally:
            self.close()
