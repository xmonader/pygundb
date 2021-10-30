import json
import asyncio
import websockets
from .backends.utils import defaultify
from .backends import Memory, Mongo, Pickle, RedisKV, DummyKV, UDB
from .backends.resolvers import is_reference, is_root_soul
from .utils import lex_from_graph, ham_mix, newuid, new_node
from .consts import METADATA, STATE, SOUL
import os
import logging
import json
import uuid

def format_put_request(soul, **kwargs):
    return {
        SOUL: newuid(),
        'put': {
            soul: new_node(soul, **kwargs)
        } 
    } 

def format_get_request(soul):
    return {
        SOUL: newuid(),
        'get': {
            SOUL: soul
        } 
    } 


class GunClient:
    def __init__(self, backend="mem", wsendpoint="ws://localhost:8000/gun"):
        self.wsendpoint = wsendpoint
        self.ws = None
        self.backend = self._init_backend(backend)
        self.graph = self.backend.recover_graph()
        if self.graph is None:
            self.graph = {}
        self.peers = []
        self.trackedids = []


    def _init_backend(self, backend_db):
        print("backenddb var: ", backend_db)
        if backend_db == "mem":
            print("mem backend")
            backend = Memory()  # Pickle()
        elif backend_db == "mongo":
            print("mongo backend")
            backend = Mongo()
        elif backend_db == "pickle":
            print("pickle backend")
            backend = Pickle()
        elif backend_db == "redis":
            backend = RedisKV()
        elif backend_db == "dummy":
            backend = DummyKV()
        elif backend_db == "udb":
            backend = UDB()
        elif backend_db == "bcdb":
            try:
                from .backends import bcdb
                backend = bcdb.BCDB()
            except:
                backend = Memory()

        return backend

    def _setup_logging(self):
        os.makedirs("clientlogs", exist_ok=True)
        putid = 0
        while os.path.exists("clientlogs/app" + str(putid) + ".log"):
            putid += 1
        logging.basicConfig(filename="clientlogs/app" + str(putid) + ".log", filemode="w", level=logging.DEBUG)
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)

    def trackid(self, id_):
        if id_ not in self.trackedids:
            self.trackedids.append(id_)
        return id_
    async def put(self, soul, **kwargs):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_put_request(soul, **kwargs)
            ch_str = json.dumps(ch)
            # print("Change: {} ".format(ch))
            await ws.send(ch_str)
            resp = await ws.recv()
            await ws.send(self.process_message(resp))
            await ws.send(resp)

    async def get(self, soul, key=None):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_get_request(soul)
            ch_str = json.dumps(ch)
            # print("Change: {} ".format(ch))
            await ws.send(ch_str)
            resp = await ws.recv()
            await ws.send(self.process_message(resp))
            await ws.send(resp)

 
    def process_message(self, msgstr):
        resp = {"ok": True}
        if msgstr is not None:
            msg = json.loads(msgstr)
            if not isinstance(msg, list):
                msg = [msg]
            overalldiff = defaultify({})
            for payload in msg:
                if isinstance(payload, str):
                    payload = json.loads(payload)
                if "put" in payload:
                    change = payload["put"]
                    msgid = payload["#"]
                    diff = ham_mix(change, self.graph)
                    uid = self.trackid(str(uuid.uuid4()))
                    resp = {"@": msgid, "#": uid, "ok": True}
                    print("DIFF:", diff)

                    for soul, node in diff.items():
                        for k, v in diff[soul][METADATA].items():
                            if isinstance(v, dict):
                                overalldiff[soul][METADATA][k] = dict(
                                    list(overalldiff[soul][METADATA][k].items()) + list(v.items())
                                )
                            else:
                                overalldiff[soul][METADATA][k] = v
                        for k, v in node.items():
                            if k == METADATA:
                                continue
                            overalldiff[soul][k] = v
                elif "get" in payload:
                    uid = self.trackid(str(uuid.uuid4()))
                    get = payload["get"]
                    msgid = payload["#"]
                    ack = lex_from_graph(get, self.backend)
                    resp = {"put": ack, "@": msgid, "#": uid, "ok": True}
            self.push_diffs(overalldiff)
            return json.dumps(resp)


    def push_diffs(self, diff):
        """
        Apply diff to reflect the changes in graph into the database.

        Diff are divided into reference updates and value updates.

        Reference updates are applied first then value updates.
        """
        ref_diff = defaultify({})
        val_diff = defaultify({})

        for soul, node in diff.items():
            ref_diff[soul][METADATA] = diff[soul][METADATA]
            for k, v in node.items():
                if k == METADATA:
                    continue
                if is_reference(v):
                    ref_diff[soul][k] = v
                else:
                    val_diff[soul][k] = v

        for soul, node in val_diff.items():
            for k, v in node.items():
                if k == METADATA or is_root_soul(k):
                    continue
                state = diff[soul][METADATA][STATE][k]
                self.backend.put(soul, k, v, state, self.graph)
        return self.graph

