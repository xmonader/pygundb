import dbm

# unix db
class UDB:
    def __init__(self, path="/tmp/gun.db"):
        self.db = dbm.open(path)


    def put(self, soul, key, value, state):
        # soul -> {field:{'state':state, 'val':val, rel: relation}}
        if soul not in self.db:
            self.db[soul] = {'_':{}}
        self.db[soul][key] = value
        self.db[soul]['_'][key] = state

    def get(self, soul, key=None):
        ret = {'#': soul, '_':{'#':soul}}

        res = self.db.get(soul, None) 
        if res is not None and key is not None:
            ret = {**ret, **res.get(key, {})}
            return ret
        elif res is not None:
            return {**ret, **res}
        else:
            return ret 
    
    def close(self):
        if self.db:
            self.db.close()

    def list(self):
        return self.db.items()