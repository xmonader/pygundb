import json
from ..consts import *
from .resolvers import *

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

        rootobjects = list(filter_root_objects(graph))
        # find its parent to get
        def do(soul, key, value, graph):
            obj = None
            if is_root_soul(soul):
                schema, obj_id = parse_schema_and_id(soul)
                obj = self.get_object_by_id(obj_id, schema)
                obj = self.set_object_attr(obj, 'id', obj_id)
                # print("object update setting attr {} with value {}".format(key, resolve_v(value, graph)))

                if key.startswith("list_"):
                    theattr = key
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
                        obj = self.set_object_attr(obj, theattr, thelist)
                    except Exception as e:
                        print(e)
                else:
                    obj = self.set_object_attr(obj, key, resolve_v(value, graph))
                print(obj)
                print("saved!!!")
                self.save_object(obj, obj_id, schema)
                return obj
            else:
                objpath = path = search(soul, graph, rootobjects)
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
                # print("*****schema:", schema)
                objdata = do(*objcontent)

                # print(objpath)

                objinfo = objpath[0]
                objpath = objpath[1:]

                obj = self.get_object_by_id(obj_id, schema)
                
                # print("objpath: ", objpath)
                while objpath:
                    attr = objpath.pop(0)
                    try:
                        obj = getattr(obj, attr)
                    except:
                        return
                obj = objdata
                self.save_object(obj, schema)
                print("success \n {}".format(obj))

        do(soul, key, value, graph)
        graph[soul][key] = value


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