import dbm
import os
from ..consts import METADATA, STATE, SOUL
# unix db
class UDB:
    def __init__(self, path="/tmp/gun.db"):
        if os.path.exists(path):
            self.db = dbm.open(path)
        else:
            self.db = dbm.open(path, "c")

    def put(self, soul, key, value, state):
        print("SETTING SOUL KEY VAL STATE TO :", soul, key, value, state, type(state))
        self.db["{soul}:{key}:{state}".format(**locals())] = value
        
    def get(self, soul, key=None):
        print("\n\n{} {} {}\n\n".format(soul, key, type(key)))
        ret = {SOUL: soul, METADATA:{SOUL:soul, STATE:{}}}
        if isinstance(key, str):
            keys = [k for k in self.db.keys() if k and k.startswith(soul+":"+key)]
        else: 
            keys = [k for k in self.db.keys() if k.startswith(soul+":")]

        for k in keys:
            sol, key, state = k.split(":")
            ret[METADATA][STATE][key] = state 
            ret[key] = self.db[k]

        return ret

    def putsoul(self, soul, souldict):
        for k,v in souldict.items():
            if k in "#_>":
                continue
            kstate = souldict.get(STATE, {}).get(STATE, {k:0})[k]
            self.put(soul, k, v, kstate)

    def __getitem__(self, soul):
        return self.get(soul, None)

    def __setitem__(self, soul, souldict):
        self.putsoul(soul, souldict)
    
    def close(self):
        if self.db:
            self.db.close()

    def list(self):
        return {k:self.db[k] for k in self.db.keys() } 
