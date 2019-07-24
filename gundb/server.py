from flask import Flask, request, send_from_directory, send_file, render_template, jsonify
from flask_sockets import Sockets
from time import sleep
import json
import os
from .utils import *
from .backends import *
from .backends.resolvers import is_root_soul, is_reference
from .backends.graph import Graph
import redis
import time 
import uuid
import sys
import traceback
import logging
from collections import defaultdict

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

    putid = 0
    while os.path.exists('app' + str(putid) + '.log'):
        putid += 1
    print(putid)
    logging.basicConfig(filename="app" + str(putid) + ".log", filemode='w', level=logging.DEBUG)                

    global peers, graph
    peers.append(ws)
    try:
        while not ws.closed:
            msgstr = ws.receive() 
            resp = {'ok':True}
            if msgstr is not None:
                msg = json.loads(msgstr)
                #print("\n\n\n received {} \n\n\n".format(msg))
                if not isinstance(msg, list):
                    msg = [msg]
                # import ipdb; ipdb.set_trace()
                rec_dd = lambda: defaultdict(rec_dd)
                overalldiff = defaultdict(rec_dd)
                for payload in msg:

                    #log = logging.getLogger()
                    #log.removeHandler(log.handlers[0])
                    #log.addHandler(logging.FileHandler('app' + str(putid) + '.log', 'w+'))
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
                            for k, v in diff[soul][METADATA].items():
                                if isinstance(v, dict):
                                    overalldiff[soul][METADATA][k] = dict(list(overalldiff[soul][METADATA][k].items()) + list(v.items()))
                                else:
                                    overalldiff[soul][METADATA][k] = v
                            for k, v in node.items():
                                if k == METADATA:
                                    continue
                                overalldiff[soul][k] = v


                        
                    elif 'get' in payload:
                        uid = trackid(str(uuid.uuid4()))
                        get = payload['get']
                        msgid = payload['#']
                        ack = lex_from_graph(get, app.backend)
                        loggraph(graph)
                        resp = {'put': ack, '@':msgid, '#':uid, 'ok':True}
                push_diffs(overalldiff, graph)                
                emit(resp)
                #print("\n\n sending resp {}\n\n".format(resp))
                emit(msg)
    except Exception as e:
        print("ERR:" ,e)
        traceback.print_exc(file=sys.stdout)
    peers.remove(ws)
    print("Peers now are: ", peers)


def push_diffs(diff, graph):
    ref_diff = defaultdict(defaultdict)
    val_diff = defaultdict(defaultdict)

    for soul, node in diff.items():
        ref_diff[soul][METADATA] = diff[soul][METADATA]
        for k, v in node.items():
            if k == METADATA:
                continue
            if is_reference(v):
                ref_diff[soul][k] = v
            else:
                val_diff[soul][k] = v
        
    Graph(graph).process_ref_diffs(ref_diff, app.backend.put)
     
    for soul, node in val_diff.items():
        for k, v in node.items():
            if k == METADATA or is_root_soul(k):
                continue
            app.backend.put(soul, k, v, diff[soul][METADATA][STATE][k], graph)
    return graph
