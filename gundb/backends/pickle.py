from pickle import load, dump
import os
import traceback
from ..consts import METADATA, STATE, SOUL

class Pickle:
    def __init__(self):
        self.db = {}
        self.dbpath = "/tmp/gun.data"
        self.load()

    
    def put(self, soul, key, value, state):
        # soul -> {field:{'state':state, 'val':val, rel: relation}}
        if soul not in self.db:
            self.db[soul] = {METADATA:{}}
        self.db[soul][key] = value
        self.db[soul][METADATA][key] = state
        
        with open(self.dbpath, "wb") as f:
            try:
                dump(self.db,  f)
            except Exception as e:
                traceback.format_exc()

    def load(self):
        default = {}
        if not os.path.exists(self.dbpath):
            self.db = {}
        else:
            with open(self.dbpath, "rb") as f:
                try:
                    self.db = load(f)
                except Exception as e:
                    print("[-] Error")
    

    def get(self, soul, key=None):
        # print("SOUL: ", soul, " KEY : ", key)
        ret = {SOUL: soul, METADATA:{SOUL:soul, STATE:{}}}
        res = None
        if soul in self.db:
            if key and isinstance(key, str):
                res = {**ret, **self.db.get(soul)}
                return res.get(key, {})
            else:
                res = {**ret, **self.db.get(soul)}
                return res

        return ret 

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
