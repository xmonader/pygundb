from collections import defaultdict
from .backend import BackendMixin
from .utils import defaultify, fix_lists, desolve
from ..consts import METADATA, SOUL, STATE
import json
ignore = '_'
LISTDATA = 'L'
MAPPING  = '[]'

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

    def delegate_list_metadatata(self, obj):
        if not isinstance(obj, dict):
            return obj
        for k, v in obj.items():
            if k == METADATA:
                continue
            if k.startswith("list_"):
                obj[k] = self.delegate_list_metadatata(v)
                obj[METADATA][LISTDATA][k][METADATA] = v[METADATA]
                mapping, result_list = self.extract_mapping_list(obj[k])
                obj[METADATA][LISTDATA][k][MAPPING] = mapping
                obj[k] = result_list
            else:
                obj[k] = self.delegate_list_metadatata(v)
        return obj

    def extract_mapping_list(self, list_obj):
        mapping = {}
        result = []
        del list_obj[METADATA]
        number_of_nones = 0
        for i, k in enumerate(list_obj.keys()):
            index = result.index(list_obj[k]) if list_obj[k] in result else -1
            if list_obj[k] == None:
                number_of_nones += 1
                mapping[k] = -1
            elif index != -1:
                mapping[k] = index
            else:
                mapping[k] = i - number_of_nones
                result.append(list_obj[k])
        return mapping, result

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
    
    def convert_to_graph(self, obj):
        if not isinstance(obj, dict):
            return obj
        result = defaultify({})
        obj = self.eliminate_lists(obj)
        for k, v in obj.items():
            result[k] = self.convert_to_graph(v)
        return result

    def eliminate_lists(self, obj):
        if METADATA not in obj or LISTDATA not in obj[METADATA]:
            return obj
        for k, v in obj[METADATA][LISTDATA].items():
            recovered_list = {METADATA: v[METADATA]}
            for orig_key, i in v[MAPPING].items():
                if i != -1:
                    recovered_list[orig_key] = obj[k][i]
            obj[k] = recovered_list
        del obj[METADATA][LISTDATA]
        return obj

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
