"""This module contains the DatabaseManagerMonitor class."""
from threading import Lock

import logging
import psycopg2


logger = logging.getLogger(__name__)


class DatabaseManagerMonitor:
    """This class contains methods to make queries to the PostgreSQL database."""
    conn: psycopg2.extensions.connection
    lock: Lock

    def __init__(self, database_url: str):
        self.conn = psycopg2.connect(dsn=database_url)
        self.lock = Lock()

    @staticmethod
    def try_to_establish_connection(database_url: str):
        """Try to establish connection to the database."""
        psycopg2.connect(dsn=database_url)

    def get_api_data(self) -> tuple:
        """Get data from the 'api' table."""
        logger.info("Getting data from the 'api' table")
        result = ()
        with self.lock:
            try:
                with self.conn:
                    with self.conn.cursor() as curs:
                        curs.execute("SELECT * FROM api;")
                        result = curs.fetchone()
            except Exception as exc:
                self.conn.rollback()
                logger.critical("Failed to get data from the 'api' table: %s - %s", type(exc), exc)

        return result

    def get_validators(self) -> list:
        """Get validators from the 'validators_info' table."""
        logger.info("Getting validators from the 'validators_info' table")
        result = []
        with self.lock:
            try:
                with self.conn:
                    with self.conn.cursor() as curs:
                        curs.execute("SELECT * FROM validators_info;")
                        result = curs.fetchall()
            except Exception as exc:
                self.conn.rollback()
                logger.critical("Failed to get validators from the 'validators_info' table: %s - %s", type(exc), exc)

        return result

    def get_holders_number(self) -> tuple:
        """Get the number of holders from the 'holder' table."""
        logger.info("Getting the number of holders")
        result = ()
        with self.lock:
            try:
                with self.conn:
                    with self.conn.cursor() as curs:
                        curs.execute("SELECT count(holder) FROM holder;")
                        result = curs.fetchone()
            except Exception as exc:
                logger.error("Failed to get the number of holders: %s - %s", type(exc), exc)
            else:
                logger.info("Successfully got the number of holders")

        return result
