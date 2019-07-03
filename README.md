# pygun
minimal `gun.js` implementation in python

## Installation
- clone the repo
- pip3 install -r requirements.txt
- execute from the repo `gunicorn -k flask_sockets.worker app:app` and you you can use -b to run on different port otherthan 8000

## Dev install
- clone the repo
- `pipenv shell`
- `pipenv install`

## Running (flasksockets server)
Execute `make run`

## Running (Gevent server)
Execute `make rungevent`


## client

you can use the reference javascript client and follow docs here https://gun.eco  or use the simple python implementation like this
```
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

```


### test client

There're multiple targets in the Makefile to use client with different backends

- `make clientdummy`
- `make clientmem`
- `make clientredis`
- `make clientudb`
- `make clientpickle`

## Examples

### Todo
There is a basic `todo.html` demo in the repo