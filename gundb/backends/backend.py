import json
import copy
from ..consts import *
from .resolvers import *
def write(data):
    fd = open('out.txt')
def uniquify(lst):
    return lst

class BackendMixin:
    def get_object_by_id(self, obj_id, schema=None):
        pass

    def set_object_attr(self, obj, attr, val):
        pass
    
    def save_object(self, obj, obj_id, schema=None):
        pass
    
    def put(self, soul, key, value, state, graph):
        if soul not in self.db:
            self.db[soul] = {METADATA:{STATE:{}}}
        self.db[soul][key] = value
        self.db[soul][METADATA][STATE][key] = state
        
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except:
                pass 

        if is_root_soul(soul): # root object
            root = soul
            path = [key]
        else: 
            path = search(soul, graph)
            if not path:
                print("soul: {} Not found\n\n".format(soul))
                return 0
            root = path[0]
            path = path[1:] + [key]

        value = resolve_v(value, graph)
        if key.startswith('list_'):
            value = uniquify(value.values())
        
        schema, index = parse_schema_and_id(root)
        root_object = self.get_object_by_id(index, schema)
        current = root_object
        for e in path[1:-1]:
            current = getattr(current, e)
        
        current[path[-1]] = value
        self.save_object(root_object, index, schema)

    def get(self, soul, key=None):
        ret = {SOUL: soul, METADATA:{SOUL:soul, STATE:{}}}

        res = None
        if soul in self.db:
            ret[METADATA] = self.db[soul][METADATA]
            if key and isinstance(key, str):
                res = {**ret, **self.db.get(soul)}
                return res.get(key, {})
            else:
                res = {**ret, **self.db.get(soul)}
                return res
        return ret 
