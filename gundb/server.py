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
from .gunserver import GUNServer
dir_path = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)

sockets = Sockets(app)

print("APP: ", app)

@app.route('/static/<path:path>')
def send_public(path):
    return send_from_directory('static' + '/' + path)

peers = []
graph = {}

@sockets.route('/gun')
def gun(ws):
    server = GUNServer()
    server.add_peer(ws)
    while not ws.closed:
        msgstr = ws.receive()
        if msgstr is not None:
            server.process_message(msgstr)  
    server.remove_peer(ws)
    print("Peers now are: ", peers)
    return None
