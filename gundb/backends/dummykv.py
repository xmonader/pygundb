import json

class DummyKV:
    def __init__(self):
        self.db = {}

    def put(self, soul, key, value, state):
        self.db["{soul}:{key}:{state}".format(**locals())] = json.dumps(value)

    def get(self, soul, key):
        print("\n\n{} {} {}\n\n".format(soul, key, type(key)))
        ret = {'#': soul, '_':{'#':soul, '>':{}}}
        if not key:
            keys = [k for k in self.db.keys() if k.startswith(soul+":")]
        else:
            keys = [k for k in self.db.keys() if k and k.startswith(soul+":"+key)]
        for k in keys:
            sol, key, state = k.split(":")
            ret['_']['>'][key] = state 
            ret[key] = self.db[k]

        return ret


    def list(self):
        return self.db.items()