from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
import json


def build_gun_server(handler):
    class GeventGunServer(WebSocketApplication):
        def on_open(self):
            print("Got client connection")
            handler.add_peer(self.ws)

        def on_message(self, message):
            resp = {"ok": True}
            if message is not None:
                handler.process_message(message)

        def on_close(self, reason):
            handler.remove_peer(self.ws)
            print("Peers now: {}".format(handler.peers))
            print(reason)

        def sendall(self, resp):
            for client in self.ws.handler.server.clients.values():
                client.ws.send(json.dumps(resp))

    return GeventGunServer
