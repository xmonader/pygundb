from collections import defaultdict
from .backend import BackendMixin
import json


def format_object_id(schema, id):
    return "{}://{}".format(schema, id)

class FakeKV:
    def __init__(self):
        self._database = {}

    def set(self, key, obj):
        self._database[key] = obj
    
    def exists(self, key):
        return key in self._database

    def get(self, key, default):
        try:
            return self._database[key]
        except:
            return default

class DummyKV(BackendMixin):
    def __init__(self):
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.kv = FakeKV()

    def get_object_by_id(self, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        return self.kv.get(full_id, {'id':obj_id})

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        self.kv.set(full_id, json.dumps(obj))

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
