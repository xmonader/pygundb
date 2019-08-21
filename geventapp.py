import sys

from gundb.geventserver import GeventGunServer
from gundb.gunrequesthandler import GUNRequestHandler
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from functools import partialmethod


def build_gun_server(handler):
    class GeventGunServerWithHandler(GeventGunServer):
        def __init__(self, *args, **kwargs):
            super().__init__(handler, *args, **kwargs)

    return GeventGunServerWithHandler


if __name__ == "__main__":
    handler = GUNRequestHandler(sys.argv[1])
    geventserverapp = WebSocketServer(("", 8000), Resource(OrderedDict([("/", build_gun_server(handler))])))
    geventserverapp.serve_forever()
