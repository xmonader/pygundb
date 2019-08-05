from collections import defaultdict
from .backend import BackendMixin
from .utils import defaultify, fix_lists
from .resolvers import desolve
from ..consts import METADATA, SOUL, STATE
import json
ignore = '_'

def format_object_id(schema, id):
    return "{}://{}".format(schema, id)

class RedisKV(BackendMixin):
    def __init__(self, host="127.0.0.1", port=6379):
        from redis import Redis
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.redis = Redis(host=host, port=port)

    def get_object_by_id(self, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        if self.redis.exists(full_id):
            return defaultify(json.loads(self.redis.get(full_id)))
        else:
            return defaultify({'id':obj_id})

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        obj = self.delegate_list_metadatata(obj)
        self.redis.set(full_id, json.dumps(obj))

    def recover_graph(self):
        root_souls = self.redis.keys(pattern="*://*")
        graph = {}
        for root_soul in root_souls:
            decoded = root_soul.decode('utf-8')
            graph[decoded] = self.recover_obj(decoded)    
        return desolve(graph)

    def recover_obj(self, key):
        db_form = defaultify(json.loads(self.redis.get(key)))
        return self.convert_to_graph(db_form)
    
    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
