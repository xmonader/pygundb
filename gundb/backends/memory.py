

class Memory:
    def __init__(self):
        self.db = {}

    def put(self, soul, key, value, state):
        # soul -> {field:{'state':state, 'val':val, rel: relation}}
        if soul not in self.db:
            self.db[soul] = {'_':{}}
        self.db[soul][key] = value
        self.db[soul]['_'][key] = state

    def get(self, soul, key=None):
        # print("SOUL: ", soul, " KEY : ", key)
        ret = {'#': soul, '_':{'#':soul, '>':{}}}
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
