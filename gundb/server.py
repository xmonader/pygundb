from flask import Flask, request, send_from_directory, send_file, render_template, jsonify
from flask_sockets import Sockets
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


dir_path = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)
backend_db = os.getenv("GUNDB", "mem")
print("backenddb var: ", backend_db)
if backend_db == "mem":
    print("mem backend")
    app.backend =  Memory() #Pickle()
elif backend_db == "mongo":
    print("mongo backend")
    app.backend = Mongo()
elif backend_db == "pickle":
    print("pickle backend")
    app.backend = Pickle()
elif backend_db == "redis":
    app.backend = RedisKV()
elif backend_db == "dummy":
    app.backend = DummyKV()
elif backend_db == "pickle":
    app.backend = Pickle()
elif backend_db == "udb":
    app.backend = UDB()

sockets = Sockets(app)

print("APP: ", app)

@app.route('/static/<path:path>')
def send_public(path):
    return send_from_directory('static' + '/' + path)

peers = []
graph = {} 
trackedids = []

def trackid(id_):
    if id_ not in trackedids:
        # print("CREATING NEW ID:::", id_)
        trackedids.append(id_)
    return id_


def emit(data):
    resp = json.dumps(data)
    # print("emitting :",  data)
    for p in peers:
        # print("Sending resp: ", resp, " to ", p)
        p.send(resp)


def loggraph(graph):
    global app
    pass
    # for soul, node in graph.items():
    #     print("\nSoul: ", soul)
    #     print("\n\t\tNode: ", node)
    #     for k, v in node.items():
    #         print("\n\t\t{} => {}".format(k, v))
    
    # print("TRACKED: ", trackedids, " #", len(trackedids))
    # print("\n\nBACKEND: ", app.backend.list())



@sockets.route('/gun')
def gun(ws):

    global peers, graph
    peers.append(ws)
    try:
        while not ws.closed:
            msgstr = ws.receive() 
            resp = {'ok':True}
            if msgstr is not None:
                msg = json.loads(msgstr)
                print("\n\n\n received {} \n\n\n".format(msg))
                if not isinstance(msg, list):
                    msg = [msg]
                # import ipdb; ipdb.set_trace()
                for payload in msg:
                    # print("payload: {}\n\n".format(payload))
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    if 'put' in payload:
                        change = payload['put']
                        msgid = payload['#']
                        diff = ham_mix(change, graph)
                        uid = trackid(str(uuid.uuid4()))
                        loggraph(graph)
                        # make sure to send error too in case of failed ham_mix

                        resp = {'@':msgid, '#':uid, 'ok':True}
                        # print("DIFF:", diff)
                        for soul, node in diff.items():
                            for k, v in node.items():
                                if k == METADATA:
                                    continue
                                graph[soul][k]=v
                            for k, v in node.items():
                                if k == METADATA:
                                    continue
                                app.backend.put(soul, k, v, diff[soul][METADATA][STATE][k], graph)

                    elif 'get' in payload:
                        uid = trackid(str(uuid.uuid4()))
                        get = payload['get']
                        msgid = payload['#']
                        ack = lex_from_graph(get, app.backend)
                        loggraph(graph)
                        resp = {'put': ack, '@':msgid, '#':uid, 'ok':True}

                emit(resp)
                print("\n\n sending resp {}\n\n".format(resp))
                emit(msg)
    except Exception as e:
        print("ERR:" ,e)
        traceback.print_exc(file=sys.stdout)
    peers.remove(ws)
    print("Peers now are: ", peers)

