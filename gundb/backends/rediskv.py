import json
import redis 


class RedisKV:
    def __init__(self, host="localhost",port=6379):
        self.r = redis.Redis(host=host, port=port) 

    def put(self, soul, key, value, state):
        key = "{soul}:{key}:{state}".format(**locals())
        self.r.set(key, json.dumps(value))


    def get(self, soul, key=None):
        ret = {'#': soul, '_':{'#':soul}}
        if key is None:
            keys = [k for k in self.r.scan_iter(soul+":"+"*")]
        else:
            keys = [k for k in self.r.scan_iter(soul+":"+key+"*")]

        for k in keys:
            sol, key, state = k.split(":")
            ret['_']['>'][key] = state 
            ret[key] = self.r.get(key)

        return ret


    def list(self):
        db = {}
        for k in self.r.keys():
            db[k] = v

        return db.items()