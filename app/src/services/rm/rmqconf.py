from dataclasses import dataclass
import pika
import os
from dotenv import load_dotenv
from src.services.logging.logging import get_logger

logger = get_logger(logger_name="RabbitMQConfig")

# Загрузите переменные из .env (уберите, если уже подгружаются глобально)
load_dotenv()


@dataclass
class RabbitMQConfig:
    """
    Конфигурационные параметры для подключения к RabbitMQ.
    
    Атрибуты:
        host: Адрес сервера RabbitMQ
        port: Порт для подключения
        virtual_host: Виртуальный хост
        username: Имя пользователя
        password: Пароль
        queue_name: Название основной очереди задач
        rpc_queue_name: Название очереди для RPC-запросов
        heartbeat: Интервал проверки соединения в секундах
        connection_timeout: Таймаут подключения в секундах
    """
    # Параметры подключения
    host: str = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    port: int = int(os.getenv('RABBITMQ_PORT', '5672'))
    virtual_host: str = os.getenv('RABBITMQ_VHOST', '/')
    
    # Параметры аутентификации
    username: str = os.getenv('RABBITMQ_DEFAULT_USER', 'guest')
    password: str = os.getenv('RABBITMQ_DEFAULT_PASS', 'guest')
    
    # Параметры очередей
    queue_name: str = os.getenv('RABBITMQ_QUEUE', 'ml_task_queue')
    rpc_queue_name: str = os.getenv('RABBITMQ_RPC_QUEUE', 'rpc_queue')
    
    # Параметры соединения
    heartbeat: int = int(os.getenv('RABBITMQ_HEARTBEAT', '30'))
    connection_timeout: int = int(os.getenv('RABBITMQ_TIMEOUT', '2'))

    def __post_init__(self) -> None:
        # Логируем параметры, которыми инициализируется конфиг
        logger.info(
            f"RabbitMQConfig инициализирован: host={self.host}, port={self.port}, "
            f"vhost={self.virtual_host}, queue={self.queue_name}, rpc_queue={self.rpc_queue_name}, "
            f"user={self.username}, heartbeat={self.heartbeat}, timeout={self.connection_timeout}"
        )

    def get_connection_params(self) -> pika.ConnectionParameters:
        """Создает параметры подключения к RabbitMQ."""
        logger.debug(
            f"Формируется параметры соединения: host={self.host}, port={self.port}, "
            f"vhost={self.virtual_host}, user={self.username}, heartbeat={self.heartbeat}, timeout={self.connection_timeout}"
        )
        try:
            return pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=pika.PlainCredentials(
                    username=self.username,
                    password=self.password
                ),
                heartbeat=self.heartbeat,
                blocked_connection_timeout=self.connection_timeout
            )
        except Exception as e:
            logger.error(f"Ошибка при формировании параметров подключения к RabbitMQ: {e}", exc_info=True)
            raise
