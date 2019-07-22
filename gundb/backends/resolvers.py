import re

SCHEME_UID_PAT = "(?P<schema>.+?)://(?P<id>.+)"

def parse_schema_and_id(s):
    m = re.match(SCHEME_UID_PAT, s)
    if m:
        return m.groupdict()['schema'], int(m.groupdict()['id']) 
    return None, None

def is_root_soul(s):
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
    return isinstance(d, dict) and '#' in d

def resolve_reference(ref, graph):
    assert(is_reference(ref))
    if not ref['#'] in graph: # The reference points to a non existent soul
        return {}

    # Shallow copy the object from a graph without its meta data.
    resolved = graph[ref['#']].copy()
    del resolved['_']
    
    for k, v in resolved.items():
        # Resolve reference items
        if not k in ignore and is_reference(v):
            resolved[k] = resolve_reference(v, graph)
    return resolved

def resolve_v(val, graph):
    """
    If val is a reference, return a copy of it with all references resolved.
    
    If val is not a reference, return it.
    """
    if is_reference(val):
        return resolve_reference(val, graph)
    else:
        return val

def copy(root, graph):
    return {k: resolve_v(v, graph) for k, v in graph.items() if k not in ignore}

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
