import sys

from gundb.geventserver import AppRunner, GeventGunServer
from gundb.gunrequesthandler import GUNRequestHandler
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from functools import partialmethod

if __name__ == "__main__":
    handler = GUNRequestHandler(sys.argv[1])
    geventserverapp = WebSocketServer(("", 8000), AppRunner(GeventGunServer, handler))
    geventserverapp.serve_forever()
