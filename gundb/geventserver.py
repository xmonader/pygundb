import sys
from collections import OrderedDict
import json

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from geventwebsocket.protocols.base import BaseProtocol
from gundb.gunrequesthandler import GUNRequestHandler
from functools import partial

class GeventRequestHandler(BaseProtocol):
    def __init__(self, app):
        super().__init__(app)

        backend = self._app.backend
        self._handler = GUNRequestHandler(backend)

    def on_open(self):
        self._handler.add_peer(self.app.ws)
        super().on_open()

    def on_close(self):
        self._handler.remove_peer(self.app.ws)
        super().on_close()

    def on_message(self, msgstr):
        self._handler.on_message(msgstr)
        super().on_message(msgstr)


class GeventGunServer(WebSocketApplication):
    protocol_class = GeventRequestHandler
    # backend = "mem