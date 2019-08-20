from flask import Flask, request, send_from_directory, send_file, render_template, jsonify
from flask_sockets import Sockets
from .gunrequesthandler import GUNRequestHandler
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)

sockets = Sockets(app)

print("APP: ", app)

@app.route('/static/<path:path>')
def send_public(path):
    return send_from_directory('static' + '/' + path)

server = GUNRequestHandler()

@sockets.route('/gun')
def gun(ws):
    server.add_peer(ws)
    while not ws.closed:
        msgstr = ws.receive()
        if msgstr is not None:
            server.process_message(msgstr)  
    server.remove_peer(ws)
    print("Peers now are: ", server.peers)
