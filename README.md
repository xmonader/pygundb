# pygun
minimal `gun.js` implementation in python

![[https://travis-ci.org/xmonader/pygundb]](https://travis-ci.org/xmonader/pygundb.png)


## Installation
- clone the repo
- pip3 install -r requirements.txt
- execute from the repo `gunicorn -k flask_sockets.worker app:app` and you can use -b to run on different port otherthan 8000

## Dev install
- clone the repo
- `poetry install`
- `poetry shell`

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


# Backends

currently we support
- redis
- mongo
- pickle db
- dummy kv
- dbm

Export GUNDB variable to one of `mem`, `redis`, `mongo`, `pickle`, `dummy`, `dbm` and invoke `make run`



## Difference from reference gun.js usage

We use Gun.js javascript client to communicate with pygundb as normal, but with some conventions

1- we work against root objects that has some schema encoding `proj.simple` for instance in the server side we use this information for object retrieval and attributes validation
2- we use root object ids `SCHEMA://ID` to retrieve the object
3- simple attributes can be updated using `put`

```javascript
      var gun = Gun("ws://127.0.0.1:8000/gun")

      let basicTest = () => {
        gun.get("proj.simple://1").put({
          "attr1": "val"
        })
        gun.get("proj.simple://2").put({
          "attr2": 5
        })

      }
```

4- for nested objects we use `.get` to work on a nested object
```javascript

      let midTest = () => {

        gun.get("proj.person://4").put({
          name: "ahmed"
        })
        gun.get("proj.person://4").put({
          "name": "ahmed"
        })
        gun.get("proj.person://4").get("email").put({
          "addr": "ahmed@gmail.com",
        })
        gun.get("proj.person://5").get("email").put({
          "addr": "andrew@gmail.com",
        })
        gun.get("proj.person://5").get("email").put({
          "addr": "dmdm@gmail.com",
        })
        gun.get("proj.person://5").get("email").put({
          "addr": "notdmdm@gmail.com",
        })

      }
```

5- working with sets of objects you need to declare they're a list using `list_` prefix for the property name

```javascript

      let advTest = () => {

        gun.get("proj.human://7").put({
          "name": "xmon"
        })
        gun.get("proj.human://7").get("phone").put({
          "model": "samsung"
        })
        gun.get("proj.human://7").get("phone").get("os").put({
          "name": "android"
        })

        gun.get("proj.human://8").put({
          "name": "richxmon"
        })
        gun.get("proj.human://8").get("phone").put({
          "model": "iphone"
        })
        gun.get("proj.human://8").get("phone").get("os").put({
          "name": "ios"
        })
        gun.get("proj.human://8").get("list_favcolors").set("white")
        gun.get("proj.human://8").get("list_favcolors").set("red")
        gun.get("proj.human://8").get("list_favcolors").set("blue")

        gun.get("proj.human://8").get("list_langs").set({
          "name": "python"
        })
        gun.get("proj.human://8").get("list_langs").set({
          "name": "ruby"
        })
```





# API usage 
pygundb [documentation](https://xmonader.github.io/pygundb/docs/api/gundb/)
