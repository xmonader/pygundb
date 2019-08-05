"""This is a module that is responsible for:
    
    1. Resolving references from the graph.
    
    2. Searching for a soul that is referenced directly or indirectly by some root object and returns its path.
    
    3. Helper function to fetch data from keys and decide its type.
"""
from .utils import defaultify
from ..consts import METADATA, SOUL
import re


SCHEME_UID_PAT = "(?P<schema>.+?)://(?P<id>.+)"

def parse_schema_and_id(s):
    """
    Returns the schema and id of the passed soul. None, None if doens't match a root soul.

    Root souls is in the form 'schem://id'
    """
    m = re.match(SCHEME_UID_PAT, s)
    if m:
        return m.groupdict()['schema'], int(m.groupdict()['id']) 
    return None, None

def is_root_soul(s):
    """
    Returns a boolean indicating whether the key s is a root soul.

    Root soul is in the form 'schema://id'
    """
    return "://" in s

def is_nested(s):
    return not is_root_soul(s)

def get_nested_soul_node(s, graph):
    return graph.get(s, {})

def filter_root_objects(graph):
    for kroot, rootnode in graph.items():
        if "://" in kroot:
            yield kroot, rootnode

ignore = ["_", ">", "#"]

def is_reference(d):
    """
    Returns a boolean indicating whether the passed argument is reference.

    A reference is a fict in the form {'#': soul}
    """
    return isinstance(d, dict) and '#' in d

def resolve_reference(ref, graph):
    """
    Resolves a reference in the form {'#': soul} from the given graph.

    Works recursively: All nested references are also resolved
    """
    assert(is_reference(ref))
    if not ref['#'] in graph: # The reference points to a non existent soul
        #Shouldn't be reached
        return {}

    # Shallow copy the object from a graph without its meta data.
    resolved = graph[ref['#']].copy()
    
    for k, v in resolved.items():
        # Resolve reference items
        if not k in ignore and is_reference(v):
            resolved[k] = resolve_reference(v, graph)
    return resolved

def resolve_v(val, graph):
    """
    If val is a reference, return a copy of it with all references resolved.

    If val is not a reference, return it as is.
    """
    if is_reference(val):
        return resolve_reference(val, graph)
    else:
        return val

def search(k, graph):
    """
    Returns a path in the graph that starts with a root object 
    and references the passed soul k. [] if non found.
    """

    def dfs(obj):
        "Returns a path in obj that ends with a reference to k"
        for key, val in obj.items():
            # Ignore the primitive values and meta data
            if key in ignore or not isinstance(val, dict):
                continue

            if val.get('#') == k: # The current value is a reference with the soul k (The one we're looking for)
                return [key]
            else:
                if is_reference(val): # The dict is a reference
                    ## FIXME: raises when running node_tests
                    try_child = dfs(graph[val['#']]) # Search in the object it references
                else:
                    try_child = dfs(val) # Otherwise, search in it directly (This case shouldn't be handled given the graph conforms to GUN rules)
                if try_child: # The reference is found in this child
                    return [key] + try_child # Shift the current key to the path and return it
        return [] # No child succeded
    
    # only root objects is tried
    for key, val in graph.items():
        if is_root_soul(key):
            try_child = dfs(val)
            if try_child:
                return [key] + try_child
    
    # No soul found :(
    return []


def desolve_obj(obj):
    """Returns the given object in gundb form along with the souls it created"""
    result = defaultify({})
    added_souls = defaultify({})
    for k, v in obj.items():
        if k != METADATA and isinstance(v, dict):
            prop_soul = v[METADATA][SOUL]
            result[k] = defaultify({SOUL: prop_soul})
            desolved_prop, added_in_prop = desolve_obj(v)
            added_souls[prop_soul] = desolved_prop
            for k, v in added_in_prop.items():
                added_souls[k] = v
        else:
            result[k] = v
    return result, added_souls


def desolve(graph):
    """resolve a graph in expanded form and convert it to gundb form"""   
    result = defaultify({})
    added_souls = defaultify({})
    for k, v in graph.items():
        prop_soul = v[METADATA][SOUL]
        result[prop_soul], added_souls_in_obj = desolve_obj(v)
        for k, v in added_souls_in_obj.items():
            added_souls[k] = v
    for k, v in added_souls.items():
        result[k] = v
    return result
