"""This module contains the ServiceParameters class implementation and constants."""
import logging
import os

import log

from database_manager_monitor import DatabaseManagerMonitor
from database_manager_token_price import DatabaseManagerTokenPrice


logger = logging.getLogger(__name__)


DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_API_PORT = '8000'
DEFAULT_PROMETHEUS_METRICS_PREFIX = 'monitor_api_'


class ServiceParameters:
    """This class contains the service parameters and methods to check and parse them."""
    api_port: int
    database_url_monitor: str
    database_url_token_price: str
    metrics_prefix: str
    token_symbol_para: str
    token_symbol_relay: str

    def __init__(self):
        log_level = os.getenv('LOG_LEVEL', DEFAULT_LOG_LEVEL)
        self._check_log_level(log_level)
        log.init_log(log_level)

        logger.info("Checking configuration parameters")

        logger.info("[ENV] LOG_LEVEL: %s", log_level)

        logger.info("[ENV] Get 'API_PORT'")
        self.api_port = int(os.getenv('API_PORT', DEFAULT_API_PORT))
        logger.info("[ENV] 'API_PORT': %s", self.api_port)

        logger.info("[ENV] Get 'PROMETHEUS_METRICS_PREFIX'")
        self.metrics_prefix= os.getenv('PROMETHEUS_METRICS_PREFIX', DEFAULT_PROMETHEUS_METRICS_PREFIX)
        logger.info("[ENV] 'PROMETHEUS_METRICS_PREFIX': %s", self.metrics_prefix)

        logger.info("[ENV] Get 'TOKEN_SYMBOL_PARA'")
        self.token_symbol_para = os.getenv('TOKEN_SYMBOL_PARA')
        if self.token_symbol_para is None:
            logger.info("[ENV] 'TOKEN_SYMBOL_PARA': not provided")
        else:
            assert self.token_symbol_para in ('glmr', 'movr'), "Inconsistent value for 'TOKEN_SYMBOL_PARA'"
            logger.info("[ENV] 'TOKEN_SYMBOL_PARA': %s", self.token_symbol_para)

        logger.info("[ENV] Get 'TOKEN_SYMBOL_RELAY'")
        self.token_symbol_relay = os.getenv('TOKEN_SYMBOL_RELAY')
        if self.token_symbol_relay is None:
            logger.info("[ENV] 'TOKEN_SYMBOL_RELAY': not provided")
        else:
            assert self.token_symbol_relay in ('dot', 'ksm'), "Inconsistent value for 'TOKEN_SYMBOL_RELAY'"
            logger.info("[ENV] 'TOKEN_SYMBOL_RELAY': %s", self.token_symbol_relay)

        logger.info("Checking the configuration parameters for the database")
        logger.info("[ENV] Get 'DATABASE_URL_MONITOR'")
        self.database_url_monitor = os.getenv('DATABASE_URL_MONITOR')
        assert self.database_url_monitor, "The 'DATABASE_URL_MONITOR' parameter is not provided"
        DatabaseManagerMonitor.try_to_establish_connection(self.database_url_monitor)
        logger.info("[ENV] 'DATABASE_URL_MONITOR': successfully got")

        self.database_url_token_price = os.getenv('DATABASE_URL_TOKEN_PRICE')
        if self.database_url_token_price is None:
            logger.info("[ENV] 'DATABASE_URL_TOKEN_PRICE': not provided")
        else:
            DatabaseManagerTokenPrice.try_to_establish_connection(self.database_url_token_price)
            logger.info("[ENV] 'DATABASE_URL_TOKEN_PRICE': successfully got")
        logger.info("Configuration parameters for the database checked")

        logger.info("Successfully checked configuration parameters")

    @staticmethod
    def _check_log_level(log_level: str):
        """Check the logger level based on the default list."""
        log_levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        if log_level not in log_levels:
            raise ValueError(f"Valid 'LOG_LEVEL_STDOUT' values: {log_levels}")
