import sys
from collections import OrderedDict
from functools import partial

from geventwebsocket import WebSocketApplication, WebSocketServer, Resource
from gundb.geventserver import GeventGunServer


if __name__ == "__main__":
    GeventGunServer.backend = sys.argv[1]
    server = WebSocketServer(
        ('', 8000),
        Resource(OrderedDict([('/',GeventGunServer)])))
    print("started..")
    server.serve_forever()
