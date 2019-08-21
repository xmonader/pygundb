from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
import json


class GeventGunServer(WebSocketApplication):
    def __init__(self, handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = handler

    def on_open(self):
        print("Got client connection")
        self.handler.add_peer(self.ws)

    def on_message(self, message):
        resp = {"ok": True}
        if message is not None:
            self.handler.process_message(message)

    def on_close(self, reason):
        self.handler.remove_peer(self.ws)
        print("Peers now: {}".format(self.handler.peers))
        print(reason)

    def sendall(self, resp):
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps(resp))
