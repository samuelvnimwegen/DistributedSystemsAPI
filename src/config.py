"""
This file contains the configuration classes for the application.

Disclaimer: This is based on our bachelor eindwerk project setup, which I also largely contributed to.
"""
import random
import string
from enum import Enum
from typing import Optional
from confz import BaseConfig


class DBConfig(BaseConfig):
    """
    Represents the database configuration.
    """
    connection_url: str


class LogLevel(Enum):
    """
    Represents the log levels.
    """
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingConfig(BaseConfig):
    """
    Represents the logging configuration.
    """
    file: Optional[str] = None
    level: Optional[LogLevel] = LogLevel.INFO
    format: Optional[str] = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"

    def get_level(self) -> Optional[str]:
        """
        Returns the log level as a string.
        """
        return self.level.value


class APIConfig(BaseConfig):
    """
    Represents the configuration for the API.
    """
    name: str = "Distributed Systems API"
    db: DBConfig
    secret_key: Optional[str] = ''.join(random.choices(string.ascii_uppercase +
                                                       string.digits, k=24))
    debug: Optional[bool] = False
    logging: LoggingConfig = LoggingConfig()
    host: Optional[str] = "0.0.0.0"
    port: Optional[int] = 8000
