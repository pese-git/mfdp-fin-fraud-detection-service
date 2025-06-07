from dataclasses import dataclass
import pika
import os

from dotenv import load_dotenv

# Загрузить .env при первом импорте этого модуля
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


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
    host: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    port: int = int(os.getenv("RABBITMQ_PORT", 5672))
    virtual_host: str = os.getenv("RABBITMQ_VHOST", "/")
    
    # Параметры аутентификации
    username: str = os.getenv("RABBITMQ_DEFAULT_USER", "rmuser")
    password: str = os.getenv("RABBITMQ_DEFAULT_PASS", "rmpassword")
    
    # Параметры очередей
    queue_name: str = os.getenv("RABBITMQ_QUEUE", "ml_task_queue")
    rpc_queue_name: str = os.getenv("RABBITMQ_RPC_QUEUE", "rpc_queue")
    
    # Параметры соединения
    heartbeat: int = int(os.getenv("RABBITMQ_HEARTBEAT", 30))
    connection_timeout: int = int(os.getenv("RABBITMQ_CONNECTION_TIMEOUT", 2))

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


@dataclass
class MLConfig:
    """Параметры MLflow, авторизации и путей к моделям."""
    mlflow_url: str = os.getenv('MLFLOW_URL')
    mlflow_tracking_token: str = os.getenv('MLFLOW_TRACKING_TOKEN', '')
    mlflow_username: str = os.getenv('MLFLOW_USERNAME', '')
    mlflow_password: str = os.getenv('MLFLOW_PASSWORD', '')
    mlflow_experiment: str = os.getenv('MLFLOW_EXPERIMENT', 'antifraud_experiment')

    # OAuth/OpenID параметры для токена
    oauth_client_id: str = os.getenv('OAUTH_CLIENT_ID')
    oauth_client_secret: str = os.getenv('OAUTH_CLIENT_SECRET')
    oauth_url: str = os.getenv('OAUTH_URL')

    # S3 настройки для mlflow
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    mlflow_s3_endpoint_url: str = os.getenv("MLFLOW_S3_ENDPOINT_URL")

    # Пути и имена моделей
    fraud_pipeline_path: str = os.getenv('PIPELINE_PATH', 'preprocessor/fraud_pipeline.joblib')
    logged_model_uri: str = os.getenv('LOGGED_MODEL_URI', 'runs:/615587bb4786452e8fc4b9b8cdb69adf/model')

RABBITMQ_CONFIG = RabbitMQConfig()
ML_CONFIG = MLConfig()