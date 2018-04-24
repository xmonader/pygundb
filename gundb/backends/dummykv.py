import json

class DummyKV:
    def __init__(self):
        self.db = {}

    def put(self, soul, key, value, state):
        if isinstance(state, dict):
            import ipdb; ipdb.set_trace()
        print("SETTING SOUL KEY VAL STATE TO :", soul, key, value, state, type(state))
        self.db["{soul}:{key}:{state}".format(**locals())] = value

    def get(self, soul, key=None):
        print("\n\n{} {} {}\n\n".format(soul, key, type(key)))
        ret = {'#': soul, '_':{'#':soul, '>':{}}}
        if isinstance(key, str):
            keys = [k for k in self.db.keys() if k and k.startswith(soul+":"+key)]
        else: 
            keys = [k for k in self.db.keys() if k.startswith(soul+":")]

        for k in keys:
            sol, key, state = k.split(":")
            ret['_']['>'][key] = state 
            ret[key] = self.db[k]

        return ret

    def putsoul(self, soul, souldict):
        for k,v in souldict.items():
            if k in "#_>":
                continue
            kstate = souldict.get("_", {}).get(">", {k:0})[k]
            self.put(soul, k, v, kstate)

    def list(self):
        return self.db.items()

    def __getitem__(self, soul):
        return self.get(soul, None)

    def __setitem__(self, soul, souldict):
        self.putsoul(soul, souldict)

