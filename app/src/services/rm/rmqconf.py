from dataclasses import dataclass
import pika
import os
from dotenv import load_dotenv

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

    def get_connection_params(self) -> pika.ConnectionParameters:
        """Создает параметры подключения к RabbitMQ."""
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
