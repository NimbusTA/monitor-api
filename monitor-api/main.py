#!/usr/bin/env python3
"""This module is an entrypoint which creates required instances and starts the server."""
import logging
import signal
import sys
from functools import partial
import prometheus_client
from flask import Flask, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from database_manager_monitor import DatabaseManagerMonitor
from database_manager_token_price import DatabaseManagerTokenPrice
from data_provider import DataProvider
from server_thread import ServerThread
from service_parameters import ServiceParameters


logger = logging.getLogger(__name__)

flask_app = Flask(__name__)
flask_app.data_provider = None


def register_prometheus_metrics_with_prefix(prefix: str):
    """Unregister default metrics and register a ProcessCollector with a prefix"""
    # Remove metrics without prefix
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
    # Add process metrics (CPU and memory) with a prefix
    prometheus_client.ProcessCollector(namespace=prefix)

    flask_app.wsgi_app = DispatcherMiddleware(flask_app.wsgi_app, {
        '/metrics': prometheus_client.make_wsgi_app(),
    })


def main():
    """Create required instances and start the server."""
    try:
        service_params = ServiceParameters()
        register_prometheus_metrics_with_prefix(service_params.metrics_prefix)
        db_mngr_monitor = DatabaseManagerMonitor(service_params.database_url_monitor)
        db_mngr_token_price = DatabaseManagerTokenPrice(service_params.database_url_token_price)
        data_provider = DataProvider(service_params, db_mngr_monitor, db_mngr_token_price)
        server = ServerThread(flask_app, service_params.api_port)
        flask_app.data_provider = data_provider
        server.start()
    except KeyboardInterrupt:
        sys.exit()
    except AssertionError as exc:
        sys.exit(f"The rule is violated: {type(exc)} - {exc}")
    except Exception as exc:
        sys.exit(f"An unexpected exception occurred: {exc}")

    signal.signal(signal.SIGTERM, partial(signal_handler, server=server, db_managers=[db_mngr_monitor, db_mngr_token_price]))
    signal.signal(signal.SIGINT, partial(signal_handler, server=server, db_managers=[db_mngr_monitor, db_mngr_token_price]))


def signal_handler(sig: int, frame=None, db_managers: list = None, server: ServerThread = None):
    """Handle a signal and terminate the process."""
    try:
        server.shutdown()
    except Exception as exc:
        logger.warning("Failed to shutdown the server: %s", exc)

    logger.info("Closing connections to databases managers")
    if db_managers is not None:
        for database_manager in db_managers:
            try:
                database_manager.conn.close()
            except Exception as exc:
                logger.warning("Failed to close the connection: %s", exc)

    sys.exit(sig)


@flask_app.route('/api')
def api():
    """Response with api data."""
    data, err = flask_app.data_provider.get_api_data()
    response = jsonify(data)
    if err is None:
        response.status = 200
    else:
        response.status = 500

    return response


@flask_app.route('/validators')
def validators():
    """Response with validators data."""
    data, err = flask_app.data_provider.get_validators()
    response = jsonify(data)
    if err is None:
        response.status = 200
    else:
        response.status = 500

    return response


if __name__ == '__main__':
    main()
