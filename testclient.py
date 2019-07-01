import asyncio
from gundb.client import GunClient

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