import json
import copy
from ..consts import *
from .resolvers import *
import logging

def uniquify(lst):
    #lst might be a list of objects
    res = []
    for r in lst:
        if r not in res:
            res.append(r)
    return res

class BackendMixin:
    def get_object_by_id(self, obj_id, schema=None):
        pass

    def set_object_attr(self, obj, attr, val):
        pass
    
    def save_object(self, obj, obj_id, schema=None):
        pass
    
    def put(self, soul, key, value, state, graph):
        logging.debug("\n\nPUT REQUEST:\nSoul: {}\nkey: {}\nvalue: {}\n\n".format(soul, key, value))
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
            logging.debug("Direct property of a root object.")
            root = soul
            path = [key]
        else: 
            logging.debug("Nested soul that must be looked for.")
            path = search(soul, graph)
            if not path: # Didn't find the soul referenced in any root object
                # Ignore the request
                logging.debug("Couldn't find soul :(")
                logging.debug("graph: {}\n\n".format(json.dumps(graph, indent = 4)))
                return 0
            root = path[0]
            path = path[1:] + [key]
        value = resolve_v(value, graph)
        if key.startswith('list_'):
            value = uniquify(value.values())
        
        schema, index = parse_schema_and_id(root)
        root_object = self.get_object_by_id(index, schema)
        current = root_object
        for e in path[0:-1]:
            try:
                current = current[e]
            except:# The path doesn't exist in the db
                # Ignore the request
                logging.debug("Couldn't traverse the database for the found path.")
                logging.debug('path: {}\n\n'.format(json.dumps([current] + path, indent = 4)))
                logging.debug("graph: {}\n\n".format(json.dumps(graph, indent = 4)))
                return 0
        logging.debug("Updated successfully!")
        if isinstance(current, list):
            current.append(value)
        else:
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
