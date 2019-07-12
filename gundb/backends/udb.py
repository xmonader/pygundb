import dbm
import json
import os
from ..consts import METADATA, STATE, SOUL
# unix db

def format_object_id(schema, id):
    return "{}://{}".format(schema, id)
class UDB:
    def __init__(self, path="/tmp/gun.db"):
        if os.path.exists(path):
            self.db = dbm.open(path)
        else:
            self.db = dbm.open(path, "c")

    def get_object_by_id(self, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        try:
            return json.loads(self.db[full_id])
        except:
            return  {'id':obj_id}
    
    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        self.db[full_id] = json.dumps(obj)
        self.savedb()

    def savedb(self):
        self.db.close()

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
