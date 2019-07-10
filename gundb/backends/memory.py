from ..consts import STATE, METADATA, SOUL

from collections import defaultdict
import re

SCHEME_UID_PAT = "(?P<schema>.+?)://(?P<id>.+)"

def parse_schema_and_id(s):
    m = re.match(SCHEME_UID_PAT, s)
    if m:
        return m.groupdict()['schema'], int(m.groupdict()['id']) 
    return None, None
class cuteobj:
    def __getattr__(self, attr):
        if attr in dir(self):
            return getattr(self, attr)
        else:
            setattr(self, attr, cuteobj())

    def __str__(self):
        return "cuteobj: {} ".format(str(self.__dict__))

class Memory:
    def __init__(self):
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.objs = defaultdict(lambda: cuteobj())

    def put(self, soul, key, value, state, graph):

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

        from pprint import pprint
        import ast
        def resolve_v(val, graph):
            # UGLY FIND ANOTHER TO FIX.
            if not isinstance(val, dict):
                try:
                    newv = ast.literal_eval(val)
                    if isinstance(newv, dict):
                        return resolve_v(newv, graph)
                    else:
                        return val
                except:
                    return val # str
            if "#" in val:
                
                referenced_name = val["#"]
                if referenced_name in graph:
                    ## double check why referenced name might not be in graph??
                    return resolve_v(graph[referenced_name], graph)
                else:
                    return {}
            return {k: resolve_v(v, graph) for k, v in val.items() if k not in ignore}

        # def search2(roots, key, graph):
        #     def search_root(root, key, graph, attrpath=[]):
        #         attrpath.append(root)
        #         tree = graph[root]
        #         for k,v in tree.items():
        #             if k == key:
        #                 attrpath.append(k)
        #                 return attrpath
        #             else:
        #                if isinstance(v, dict) and "#" in v:
        #                    potential_root = v["#"]
        #                    res = search_root(potential_root, key, graph, attrpath)
        #         return []

            
        #     for root in roots:
        #         thepath = search_root(root, key, graph)
        #         if thepath:
        #             break
        #     if thepath:
        #         pass

        def search(k, graph):
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

        rootobjects = list(filter_root_objects(graph))
        # find its parent to get
        def do(soul, key, value, graph):
            # print(json.dumps(graph, indent=4, sort_keys=True))
            obj = None
            model = None
            if is_root_soul(soul):
                schema, obj_id = parse_schema_and_id(soul)
                obj = self.objs.get(obj_id, cuteobj())
                obj.id = obj_id
                print(":::=> object update setting attr {} with value {}".format(key, resolve_v(value, graph)))

                if key.startswith("list/"):
                    theattr = key[len("list/"):]
                    resolved_list = resolve_v(value, graph)
                    def hash_dict(adict):
                        return str(adict)

                    d_as_list = resolved_list.values()
                    unique_items = []
                    added = set()
                    for k, v in resolved_list.items():
                        if str(v) not in added:
                            added.add(str(v))
                            unique_items.append(v)

                    thelist = unique_items
                    try:
                        setattr(obj, theattr, thelist)
                    except Exception as e:
                        print(e)
                else:
                    setattr(obj, key, resolve_v(value, graph))
                print("saved!!!")
                print(obj)
                self.objs[obj.id] = obj
                return obj
            else:
                objpath = path = search(soul, graph)
                if not objpath:
                    # FIXME doesn't work 

                    """
                        put bcdb => soul jxvd6ufqyCFeQ9mtcpwJ key jxvd6ufkPTDohIx value white state 1562649540756
                        {
                            "jxvd6ufqyCFeQ9mtcpwJ": {
                                "_": {
                                    "#": "jxvd6ufqyCFeQ9mtcpwJ",
                                    ">": {
                                        "jxvd6ufkPTDohIx": 1562649540756
                                    }
                                },
                                "jxvd6ufkPTDohIx": "white"
                            }
                        }
                        [---]can't find : jxvd6ufqyCFeQ9mtcpwJ jxvd6ufkPTDohIx white
                    """
                    print("[---]can't find :", soul, key, value) 
                    return
                objcontent = path + [{"#":soul}, graph]

                schema, obj_id = parse_schema_and_id(objpath[0])
                if not schema:
                    return 
                print("*****schema:", schema)
                objdata = do(*objcontent)

                print(objpath)

                objinfo = objpath[0]
                objpath = objpath[1:]

                obj = self.db.get(obj_id)
                
                print("objpath: ", objpath)
                while objpath:
                    attr = objpath.pop(0)
                    try:
                        obj = getattr(obj, attr)
                    except Exception as e:
                        print("err: ", e)
                obj = objdata
                self.objs[obj.id] = obj
                print("success.....!!!!!", obj)
                for objid, obj in self.objs.items():
                    print(obj)
        do(soul, key, value, graph)

        graph[soul][key] = value
        # print(graph)





        # soul -> {field:{'state':state, 'val':val, rel: relation}}
        if soul not in self.db:
            self.db[soul] = {METADATA:{}}
        self.db[soul][key] = value
        self.db[soul][METADATA][key] = state

    def get(self, soul, key=None):
        # print("SOUL: ", soul, " KEY : ", key)
        ret = {SOUL: soul, METADATA:{SOUL:soul, STATE:{}}}
        res = None
        if soul in self.db:
            if key and isinstance(key, str):
                res = {**ret, **self.db.get(soul)}
                return res.get(key, {})
            else:
                res = {**ret, **self.db.get(soul)}
                return res

        return ret 

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
