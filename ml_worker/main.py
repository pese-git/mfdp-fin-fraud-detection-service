import logging
import sys
import time

import pika
from pika.exceptions import AMQPConnectionError
from rmq.rmqconf import RabbitMQConfig
from rmq.rmqworker import RabbitMQLlmWorker

# Настраиваем базовую конфигурацию логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # Устанавливаем уровень логирования DEBUG  # Задаем формат сообщений лога

logger = logging.getLogger(__name__)


def create_worker(mode: str, config: RabbitMQConfig) -> RabbitMQLlmWorker:
    """Create appropriate worker instance based on mode."""
    return RabbitMQLlmWorker(config)


def run_worker(worker: RabbitMQLlmWorker) -> None:
    """Run worker with reconnection logic."""
    while True:
        try:
            if not worker.connection or not worker.connection.is_open:
                logger.info("Connecting to RabbitMQ...")
                worker.connect()
            logger.info("Starting message consumption...")
            worker.start_worker()

        except AMQPConnectionError as e:
            logger.error(f"Connection error: {e}")
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

        time.sleep(1)


def main() -> int:
    mode = "ml"
    logger.info(f"Starting worker in {mode} mode")

    worker = None
    try:
        config = RabbitMQConfig()
        worker = create_worker(mode, config)
        run_worker(worker)
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
