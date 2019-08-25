import sys

from geventwebsocket import WebSocketServer
from gundb.geventserver import AppRunner, GeventGunServer
from gundb.gunrequesthandler import GUNRequestHandler

if __name__ == "__main__":
    handler = GUNRequestHandler(sys.argv[1])
    geventserverapp = WebSocketServer(("", 8000), AppRunner(GeventGunServer, handler))
    geventserverapp.serve_forever()
