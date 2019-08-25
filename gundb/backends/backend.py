import json
import logging

from ..consts import METADATA, SOUL, STATE, LISTDATA, MAPPING
from .resolvers import is_root_soul, parse_schema_and_id, resolve_v, search
from .utils import defaultify


class BackendMixin:
    def get_object_by_id(self, obj_id, schema=None):
        """Returns the object from the db as a defaultdict in the db form.

        Args:
            obj_id (int): The id of the object.
            schema (str, optional): The schema of the object to be retrieved. Defaults to None.
        """

    def set_object_attr(self, obj, attr, val):
        """sets the object's atribute (not used).

        Args:
            obj (Object): Object.
            attr (str): Attribute.
            val (any): Value.
        """

    def save_object(self, obj, obj_id, schema=None):
        """Receives an object in gundb form and stores it in the backend database.

        Args:
            obj (defaultdict): The object to be saved.
            obj_id (int): Its id.
            schema (str, optional): Its schema url. Defaults to None.
        """

    def recover_graph(self):
        """
        Recovers the graph from the db.
        It simply retrieves all the objects in the form schema://id and converts it to gundb from.
        """

    def put(self, soul, key, value, state, graph):
        """
        Handles a put request.
        Reflect the update graph[soul][key] = value in the database.
        First, it finds the root object to which the soul belongs, \
                then depending if a list is involved in the path from the root to the changed property, \
                update_normal or update_list is called.

        List removal is converted to a put request that modifies the associated value to None. It's eliminated by the function eliminate_nones.
        
        Args:
            soul  (str) : The soul in which the property will be changed.
            key   (str) : The key that will be changed.
            value       : The new value associated with the key.
            state (dict): The state.
            graph (dict): The updated GUN graph.
        """

        logging.debug(
            "\n\nPUT REQUEST:\nSoul: {}\nkey: {}\nvalue: {}\n graph:{}\n\n".format(
                soul, key, value, json.dumps(graph, indent=4)
            )
        )
        if soul not in self.db:
            self.db[soul] = {METADATA: {STATE: {}}}
        self.db[soul][key] = value
        self.db[soul][METADATA][STATE][key] = state

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except:
                pass

        if is_root_soul(soul):  # root object
            logging.debug("Direct property of a root object.")
            root = soul
        else:
            logging.debug("Nested soul that must be looked for.")
            root = search(soul, graph)
            if not root:  # Didn't find the soul referenced in any root object
                # Ignore the request
                logging.debug("Couldn't find soul :(")
                # logging.debug("graph: {}\n\n".format(json.dumps(graph, indent = 4)))
                return
        schema, index = parse_schema_and_id(root)
        root_object = resolve_v({SOUL: root}, graph)
        self.save_object(defaultify(root_object), index, schema)
        print("RECOVERD GRAPH: {}".format(json.dumps(self.recover_graph(), indent=4)))

    def get(self, soul, key=None):
        ret = {SOUL: soul, METADATA: {SOUL: soul, STATE: {}}}

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

    def delegate_list_metadatata(self, obj):
        """
        Moves the state object of all lists in obj to the parent object and converts it to a list.

        Args:
            obj (defaultdict): The dict representing the obj in gundb form.

        Returns:
            defaultdict: The object after delegating the list data and converting it to actual python lists.
        """
        if not isinstance(obj, dict):
            return obj
        result = defaultify({})
        for k, v in obj.items():
            if k.startswith("list_"):
                result[k] = self.delegate_list_metadatata(v)
                result[METADATA][LISTDATA][k][METADATA] = v[METADATA]
                mapping, result_list = self.extract_mapping_list(result[k])
                result[METADATA][LISTDATA][k][MAPPING] = mapping
                result[k] = result_list
            elif k == METADATA:
                result[k] = v
            else:
                result[k] = self.delegate_list_metadatata(v)
        return result

    def extract_mapping_list(self, list_obj):
        """
        It receives an object whose key starts with list_.
        Then it converts it to a list by extracting the values of the list_obj.
        The reverse operation is done by storing the mapping between the keys and
             the indexes of values in the newly created list.

        Args:
            list_obj (defaultdict): A dict in gundb form that represents a list.

        Returns:
            defaultdict, list: The mapping between the values
        """
        mapping = defaultify({})
        result = []
        keys = list(list_obj.keys())
        keys.remove(METADATA)
        number_of_nones = 0
        for i, k in enumerate(keys):
            index = result.index(list_obj[k]) if list_obj[k] in result else -1
            if list_obj[k] is None:
                number_of_nones += 1
                mapping[k] = -1
            elif index != -1:
                mapping[k] = index
            else:
                mapping[k] = i - number_of_nones
                result.append(list_obj[k])
        return mapping, result

    def convert_to_graph(self, obj):
        """
        Receives a dict representing the graph in the db form and converts it to gundb form.
        In the db form, the lists are stored as actual lists and the metadata is delegated.

        Args:
            obj (defaultdict): The object in the db form.

        Returns:
            defaultdict: The graph in the gundb form.
        """
        if not isinstance(obj, dict):
            return obj
        result = defaultify({})
        obj = self.eliminate_lists(obj)
        for k, v in obj.items():
            result[k] = self.convert_to_graph(v)
        return result

    def eliminate_lists(self, obj):
        """Restores the list by fetchnig the mapping and its metadata and converts the list to gundb obj.
        
        Args:
            obj (defaultdict): An object in the db form.
        
        Returns:
            defaultdict: The first level of lists eliminated.
        """
        if METADATA not in obj or LISTDATA not in obj[METADATA]:
            return obj
        result = obj.copy()
        for k, v in obj[METADATA][LISTDATA].items():
            recovered_list = {METADATA: v[METADATA]}
            for orig_key, i in v[MAPPING].items():
                if i != -1:
                    recovered_list[orig_key] = obj[k][i]
            result[k] = recovered_list
        del result[METADATA][LISTDATA]
        return result
