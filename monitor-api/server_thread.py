"""This module contains the ServerThread class."""
import logging

from threading import Thread
from werkzeug.serving import make_server


logger = logging.getLogger(__name__)


class ServerThread(Thread):
    """This class describes a thread, which contains methods to start and shutdown a server."""
    def __init__(self, app, port: int, ip_address: str = '0.0.0.0'):
        Thread.__init__(self)
        logger.info("Starting the server on %s:%s", ip_address, port)
        self.server = make_server(ip_address, port, app, threaded=True)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        """Start the server."""
        self.server.serve_forever()

    def shutdown(self):
        """Shutdown the server."""
        self.server.shutdown()
