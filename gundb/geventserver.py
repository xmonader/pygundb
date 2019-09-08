from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from time import sleep
import json
import os
from .utils import *
from .backends import *
import redis
import time 
import uuid
import sys
import traceback
from .gunrequesthandler import GUNRequestHandler


server = GUNRequestHandler()

class GeventGunServer(WebSocketApplication):
    def on_open(self):
        print("Got client connection")
        server.add_peer(self.ws)

    def on_message(self, message):
        resp = {'ok':True}
        if message is not None:
            server.process_message(message)

    def on_close(self, reason):
        server.remove_peer(self.ws)
        print("Peers now: {}".format(server.peers))
        print(reason)

    def sendall(self, resp):
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps(resp))

geventserverapp = WebSocketServer(
    ('', 8000),
    Resource(OrderedDict([('/', GeventGunServer)]))
)

