import sys
from collections import OrderedDict

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from gundb.geventserver import AppRunner, GeventGunServer
from gundb.gunrequesthandler import GUNRequestHandler
from functools import partial

if __name__ == "__main__":
    handler = GUNRequestHandler(sys.argv[1])

    server = WebSocketServer(
        ('', 8000),
        Resource(OrderedDict([('/', partial(GeventGunServer, handler))]))
    )
    server.serve_forever()
