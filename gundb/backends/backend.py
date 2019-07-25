import json
import copy
from ..consts import *
from .resolvers import *
from .utils import *
import logging

#def uniquify(lst):
#    #lst might be a list of objects
#    res = []
#    for r in lst:
#        if r not in res:
#            res.append(r)
#    return res

class BackendMixin:
    def get_object_by_id(self, obj_id, schema=None):
        pass

    def set_object_attr(self, obj, attr, val):
        pass
    
    def save_object(self, obj, obj_id, schema=None):
        pass
    
    def put(self, soul, key, value, state, graph):
        """
        Handles a put request.
        Reflect the update graph[soul][key] = value in the database.
        First, it finds the root object to which the soul belongs, \
                then depending if a list is involved in the path from the root to the changed property, \
                update_normal or update_list is called.

        Args:
            soul  (str) : The soul in which the property will be changed.
            key   (str) : The key that will be changed.
            value       : The new value associated with the key.
            state (dict): The state.
            graph (dict): The updated GUN graph.
        """

        logging.debug("\n\nPUT REQUEST:\nSoul: {}\nkey: {}\nvalue: {}\n graph:{}\n\n".format(soul, key, value, json.dumps(graph, indent = 4)))
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
                #logging.debug("graph: {}\n\n".format(json.dumps(graph, indent = 4)))
                return 0
            root = path[0]
            path = path[1:] + [key]
        schema, index = parse_schema_and_id(root)
        root_object = self.get_object_by_id(index, schema)
        value = fix_lists(resolve_v(value, graph))
        list_index = get_first_list_prop(path)
        if list_index != -1:
            self.update_list(root, path[:list_index + 1], soul, root_object, schema, index, graph)
        else:
            self.update_normal(path, value, root_object, schema, index)
        logging.debug("Updated successfully!")
        

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


    def update_list(self, root, path, soul, root_object, schema, index, graph):
        """
        Update list property.
        
        Walks through the graph first to retrieve the soul of the list, \
            Then updates the list in the db by resolving it first from the graph.
        """
        current = graph[root]
        for e in path[:-1]:
            current = graph[current[e][METADATA][SOUL]]

        list_id = current[path[-1]][SOUL]
        self.update_normal(path, fix_lists(resolve_v({SOUL: list_id}, graph)), root_object, schema, index)
        return 0

    def update_normal(self, path, value, root_object, schema, index):
        """
        Update a normal property.

        Args:
            path        (list): The keys to follow from root_object to reach the desired path.
            value             : The value to be stored in this location.
            root_object (dict): The root object from GUN graph.
            schema      (str) : The schema of the root soul. Root soul is in the format schema://index
            index       (str) : The index of the root soul.
        """
        key = path[-1]
        if key.startswith('list_'):
            value = listify(value)
        current = root_object
        for e in path[:-1]:
            try:
                current = current[e]
            except:# The path doesn't exist in the db
                # Ignore the request
                logging.debug("Couldn't traverse the database for the found path.")
                logging.debug('path: {}\n\n'.format(json.dumps([current] + path, indent = 4)))
                #logging.debug("graph: {}\n\n".format(json.dumps(graph, indent = 4)))
                return 0
        current[path[-1]] = value
