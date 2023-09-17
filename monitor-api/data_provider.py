"""This module contains the DataProvider class."""
import logging

from datetime import datetime
from typing import List, Tuple, Union

from database_manager_monitor import DatabaseManagerMonitor
from database_manager_token_price import DatabaseManagerTokenPrice
from service_parameters import ServiceParameters


logger = logging.getLogger(__name__)

PRICE_PRECISION_DIVISOR = 1_000_000
REWARDS_PRECISION_DIVISOR = 1_000_000_000_000


class DataProvider:
    """This class contains methods for getting data for API"""
    db_manager_monitor: DatabaseManagerMonitor
    db_manager_token_price: DatabaseManagerTokenPrice

    def __init__(self, service_params: ServiceParameters,
                 db_manager_monitor: DatabaseManagerMonitor, db_manager_token_price: DatabaseManagerTokenPrice):
        self.db_manager_monitor = db_manager_monitor
        self.db_manager_token_price = db_manager_token_price
        self.service_params = service_params

    def get_api_data(self) -> Tuple[dict, Union[None, Exception]]:
        """Get api data from the database and return the result as a JSON string"""
        logger.info("Request api data")
        # The 'api' table schema:
        # 0 - apr - FLOAT
        # 1 - apr_per_month - FLOAT
        # 2 - apr_per_week - FLOAT
        # 3 - estimated_apy - FLOAT
        # 4 - inflation_rate - FLOAT
        # 5 - total_rewards - uint_256
        # 6 - total_losses - uint_256
        # 7 - total_staked_relay - uint_256
        # 8 - total_supply - uint_256
        response = {}
        query = self.db_manager_monitor.get_api_data()
        if not query:
            logger.error("Failed to get api data")
            return response, Exception("failed to get api data")

        holders_number = self.db_manager_monitor.get_holders_number()
        if not holders_number:
            logger.error("Failed to get holders numbers")
            return response, Exception("failed to get holders number")

        if (
            self.service_params.database_url_token_price is None
            or self.service_params.token_symbol_relay is None
            or self.service_params.token_symbol_para is None
        ):
            logger.warning("Using the static price")
            token_price_para = 0
            token_price_relay = 0
        else:
            date = datetime.now().strftime("%d-%m-%Y")
            token_price_para = self.db_manager_token_price.get_token_price(self.service_params.token_symbol_para, date)
            token_price_relay = self.db_manager_token_price.get_token_price(self.service_params.token_symbol_relay, date)
        token_price_para = 0 if not token_price_para else token_price_para[0]
        token_price_relay = 0 if not token_price_relay else token_price_relay[0]

        response = {
            'APRPerMonth': query[1],
            'estimatedAPY': query[3],
            'stakers': holders_number[0],
            'pricePara': token_price_para / PRICE_PRECISION_DIVISOR,
            'priceRelay': token_price_relay / PRICE_PRECISION_DIVISOR,
            'totalStaked': {
                'token': int(query[8]) / REWARDS_PRECISION_DIVISOR,
                'usd': int(query[8]) / REWARDS_PRECISION_DIVISOR * token_price_relay / PRICE_PRECISION_DIVISOR,
            },
            'totalRewards': int(query[5]) / REWARDS_PRECISION_DIVISOR,
        }

        return response, None

    def get_validators(self) -> Tuple[List[dict], Union[None, Exception]]:
        """Get validators from the database and return the result as a JSON string"""
        logger.info("Request validators info")
        # The 'validators_info' table schema:
        # 0 - active_stake - uint_256
        # 1 - ledger - TEXT
        # 2 - stash - TEXT
        # 3 - validators - TEXT
        query_result = self.db_manager_monitor.get_validators()
        response = []
        for row in query_result:
            response.append({
                'active_stake': int(row[0]),
                'ledger': row[1],
                'stash': row[2],
                'validators': [] if not row[3] else row[3].split(','),
            })
        if not response:
            logger.error("Failed to get validators info")
            return response, Exception("failed to get validators info")

        return response, None
