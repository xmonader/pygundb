import json
import redis 
from ..consts import *

class RedisKV:
    def __init__(self, host="localhost",port=6379):
        self.r = redis.Redis(host=host, port=port) 

    def put(self, soul, key, value, state):
        key = "{soul}:{key}:{state}".format(**locals())
        self.r.set(key, value)


    def get(self, soul, key=None):
        ret = {SOUL: soul, METADATA:{SOUL:soul}}
        if key is None:
            keys = [k for k in self.r.scan_iter(soul+":"+"*")]
        else:
            keys = [k for k in self.r.scan_iter(soul+":"+key+"*")]

        for k in keys:
            sol, key, state = k.split(":")
            ret[METADATA][STATE][key] = state 
            ret[key] = self.r.get(key)

        return ret


    def list(self):
        db = {}
        for k in self.r.keys():
            db[k] = self.r.get(k)

        return db.items()

    def __getitem__(self, soul):
        return self.get(soul, None)
