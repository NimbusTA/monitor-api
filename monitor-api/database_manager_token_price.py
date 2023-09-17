"""This module contains the DatabaseManagerTokenPrice class."""
from threading import Lock

import logging
import psycopg2


logger = logging.getLogger(__name__)


class DatabaseManagerTokenPrice:
    """A class that provides the method to get token prices from the PostgreSQL database."""
    conn: psycopg2.extensions.connection
    cursor: psycopg2.extensions.cursor
    lock: Lock

    def __init__(self, dsn: str):
        self.conn = psycopg2.connect(dsn=dsn)
        self.lock = Lock()

    @staticmethod
    def try_to_establish_connection(dsn: str):
        """Try to establish connection to the database"""
        psycopg2.connect(dsn=dsn)

    def get_token_price(self, postfix: str, date: str) -> tuple:
        """Select a price from the token_price_{postfix} table"""
        logger.debug("[SELECT] token_price_%s: %s", postfix, date)
        result = ()
        with self.lock:
            try:
                with self.conn:
                    with self.conn.cursor() as curs:
                        curs.execute(f"SELECT price FROM token_price_{postfix} WHERE token_price_{postfix}.date = %s", (date,))
                        result = curs.fetchone()
            except Exception as exc:
                logger.error("Failed to get token price from the database. %s: %s", date, exc)

        return result
