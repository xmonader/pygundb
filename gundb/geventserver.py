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


peers = []
graph = {} 
trackedids = []

class App:
    def __init__(self, backend):
        self.backend = backend


app = App(DummyKV())

def trackid(id_):
    if id_ not in trackedids:
        print("CREATING NEW ID:::", id_)
        trackedids.append(id_)
    return id_

def emit(data):
    resp = json.dumps(data)
    for p in peers:
        print("Sending resp: ", resp, " to ", p)
        p.send(resp)

def loggraph(graph):
    global app
    for soul, node in graph.items():
        print("\nSoul: ", soul)
        print("\n\t\tNode: ", node)
        for k, v in node.items():
            print("\n\t\t{} => {}".format(k, v))
    
    print("TRACKED: ", trackedids, " #", len(trackedids))
    print("\n\nBACKEND: ", app.backend.list())




class GeventGunServer(WebSocketApplication):
    def on_open(self):
        print("Got client connection")

    def on_message(self, message):
        resp = {'ok':True}
        if message is not None:
            msg = json.loads(message)
            if not isinstance(msg, list):
                msg = [msg]
            for payload in msg:
                if isinstance(payload, str):
                    payload = json.loads(payload)
                if 'put' in payload:
                    change = payload['put']
                    soul = payload['#']
                    diff = ham_mix(change, graph)
                    uid = trackid(str(uuid.uuid4()))
                    loggraph(graph)
                    resp = {'@':soul, '#':uid, 'ok':True}
                    print("DIFF:", diff)
                    for soul, node in diff.items():
                        for k, v in node.items():
                            if k == "_":
                                continue
                            val = json.dumps(v)
                            app.backend.put(soul, k, v, diff[soul]['_']['>'][k])

                elif 'get' in payload:
                    get = payload['get']
                    soul = get['#']
                    ack = lex_from_graph(get, app.backend)
                    uid = trackid(str(uuid.uuid4()))
                    loggraph(graph)
                    resp = {'put': ack, '@':soul, '#':uid, 'ok':True}

                self.sendall(resp)
                self.sendall(msg)

        self.ws.send(message)

    def on_close(self, reason):
        print(reason)

    def sendall(self, resp):
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps(resp))

geventserverapp = WebSocketServer(
    ('', 8000),
    Resource(OrderedDict([('/', GeventGunServer)]))
)

