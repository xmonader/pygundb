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

def resolve_v(val, graph):
    # UGLY FIND ANOTHER TO FIX.
    if not isinstance(val, dict):
        return val # str
    if "#" in val:
        referenced_name = val["#"]
        if referenced_name in graph:
            ## double check why referenced name might not be in graph??
            return resolve_v(graph[referenced_name], graph)
        else:
            return {}
    return {k: resolve_v(v, graph) for k, v in val.items() if k not in ignore}

def search(k, graph, rootobjects):
    # DON'T CHANGE: CHECK WITH ME OR ANDREW
    roots = list(rootobjects)
    def inner(k, current_key, current_node, graph, path=None):
        # print("path in inner: ", path)
    
        if not isinstance(current_node, dict):
            return []   
        if not path:
            path = []
    
        if current_key:
            path.append(current_key)

        for key, node in current_node.items():
            
            # print("node: {} ".format(node))
            # print("key {}".format(key))
            if key in ">_":
                continue

            if isinstance(node, dict) and node.get("#") == k:
                path.append(key)
                return path
            
            res = inner(k, key, node, graph, path)
            if res:
                return res
            else:
                pass
                # print("path now : ", path)
                
        if current_key:
            path.pop()
        return []
        
    return inner(k, None, graph, roots, None)