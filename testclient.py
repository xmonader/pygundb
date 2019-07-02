import asyncio
from gundb.client import GunClient
from gundb.backends import *

async def test():
    import sys
    argv = sys.argv
    backend = DummyKV()
    if "dummy" in argv:
        backend = DummyKV()
    elif "memory" in argv:
        backend = Memory()
    elif "redis" in argv:
        backend = RedisKV()
    elif "udb" in argv:
        backend = UDB()
    elif "pickle" in argv:
        backend = Pickle()
    
    c = GunClient()
    c.backend = backend
    print(c.backend.db)
    await c.put('box', w=101, h=30)
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