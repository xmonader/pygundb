import json
import asyncio
import websockets
from .utils import newuid, new_node, ham_mix
from .backends import *

def format_put_request(soul, **kwargs):
    ch = {
        '#': newuid(),
        'put': {
            soul: new_node(soul, **kwargs)
        } 
    }
    return ch 

def format_get_request(soul):
    ch = {
        '#': newuid(),
        'get': {
            '#': soul
        } 
    }
    return ch 


class GunClient:
    def __init__(self, wsendpoint="ws://localhost:8000/gun"):
        self.wsendpoint = wsendpoint
        self.ws = None
        self.backend = Memory()

    async def put(self, soul, **kwargs):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_put_request(soul, **kwargs)
            ch_str = json.dumps(ch)
            # print("Change: {} ".format(ch))
            await ws.send(ch_str)
            resp = await ws.recv()
            # print("RESP: {} ".format(resp))
            return resp
        
    async def get(self, soul, k=None):
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
            soul = loaded['#']
            diff = ham_mix(change, self.backend)

            resp = {'@':soul, '#':newuid(), 'ok':True}
            # print("DIFF:", diff)

            for soul, node in diff.items():
                for k, v in node.items():
                    if k == "_":
                        continue
                    self.backend.put(soul, k, v, diff[soul]['_']['>'][k])
            return self.backend.get(soul, k)

async def test():

    c = GunClient()
    print(c.backend)
    await c.put('box', w=10, h=20)
    box = await c.get('box')
    print("Box is: ", box)
    w = await c.get('box', 'w')
    print("W is : ", w)
    print(c.backend)

def cltest():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())


if __name__ == "__main__":
    cltest()