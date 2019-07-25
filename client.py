import json
import asyncio
import websockets
from gundb.utils import * 
from gundb.backends import *
from gundb.consts import METADATA, SOUL, STATE

def format_put_request(soul, **kwargs):
    ch = {
        SOUL: newuid(),
        'put': {
            soul: new_node(soul, **kwargs)
        } 
    }
    return ch 

def format_get_request(soul):
    ch = {
        SOUL: newuid(),
        'get': {
            SOUL: soul
        } 
    }
    return ch 


class GunClient:
    def __init__(self, wsendpoint="ws://localhost:8000/gun"):
        self.wsendpoint = wsendpoint
        self.ws = None
        self.backend = DummyKV()

    async def put(self, soul, **kwargs):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_put_request(soul, **kwargs)
            ch_str = json.dumps(ch)
            # print("Change: {} ".format(ch))
            await ws.send(ch_str)
            resp = await ws.recv()
            # print("RESP: {} ".format(resp))
            return resp
        
    async def get(self, soul, key=None):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_get_request(soul)
            ch_str = json.dumps(ch)
            # print("Change: {} ".format(ch))
            await ws.send(ch_str)
            resp = await ws.recv()
            loaded = json.loads(resp)
            # print("RESP: {} ".format(resp))
            change = loaded['put']
            # print("CHANGE IS: ", change)
            soul = loaded[SOUL]
            diff = ham_mix(change, self.backend)

            resp = {'@':soul, SOUL:newuid(), 'ok':True}
            # print("DIFF:", diff)

            for soul, node in diff.items():
                for k, v in node.items():
                    if k == METADATA:
                        continue
                    kstate = 0
                    try:
                        kstate = diff[soul][METADATA][STATE][k]
                    except KeyError: 
                        pass 
                    else:
                        print("KSTATE: ", kstate)
                    self.backend.put(soul, k, v, kstate)
            return self.backend.get(soul, key)

async def test():

    c = GunClient()
    print(c.backend.db)
    await c.put('box', w=10, h=20)
    box = await c.get('box')
    print("Box is: ", box)
    w = await c.get('box', 'w')
    print("W is : ", w)
    print(c.backend.db)

def cltest():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())


if __name__ == "__main__":
    cltest()
