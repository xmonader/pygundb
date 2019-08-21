import sys

from gundb.geventserver import build_gun_server
from gundb.gunrequesthandler import GUNRequestHandler
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from functools import partialmethod

if __name__ == "__main__":
    handler = GUNRequestHandler(sys.argv[1])
    geventserverapp = WebSocketServer(("", 8000), Resource(OrderedDict([("/", build_gun_server(handler))])))
    geventserverapp.serve_forever()
