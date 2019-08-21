from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
import json


class GeventGunServer(WebSocketApplication):
    def __init__(self, ws, handler):
        super().__init__(ws)
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


class AppRunner:
    def __init__(self, app, handler):
        self.app = app
        self.handler = handler

    def __call__(self, environ, start_response):
        is_websocket_call = "wsgi.websocket" in environ
        current_app = self.app

        if is_websocket_call:
            ws = environ["wsgi.websocket"]
            current_app = current_app(ws, self.handler)
            current_app.handle()
        return []
