import re
import json
from ..consts import STATE, LISTDATA, MAPPING, SOUL, METADATA
from .backend import BackendMixin
from .utils import defaultify
from .resolvers import desolve
import Jumpscale
from Jumpscale import j
from collections import defaultdict

BCDBMETADATA = "metadata"
SCHEME_UID_PAT = "(?P<schema>.+?)://(?P<id>.+)"

schemas = [
    """
@url = proj.todoitem
a= "" (S)
title* = "" (S)
done = False (B)
""",
    """
@url = proj.todolist
a= "" (S)
name* = "" (S)
list_todos = (LO) !proj.todoitem
""",
    """
@url = proj.simple
metadata = "" (S)
attr1* = "" (S)
attr2 = 0 (I)
list_mychars = (LS) 
""",
    """
@url = proj.email
metadata = "" (S)
addr* = "" (S)
""",
    """
@url = proj.person
metadata = "" (S)
name* = "" (S)
email = (O) !proj.email
""",
    """
@url = proj.os
metadata = "" (S)
name* = "" (S)
""",
    """
@url = proj.phone
metadata = "" (S)
model* = "" (S)
os = (O) !proj.os
""",
    """
@url = proj.lang
metadata = "" (S)
name* = ""
""",
    """
@url = proj.human
metadata = "" (S)
name* = "" (S)
list_favcolors = (LS)
list_langs = (LO) !proj.lang
phone = (O) !proj.phone
""",
    """
@url = proj.post
metadata = "" (S)
name = "" (S)
title* = "" (S)
body = "" (S)
""",
    """
@url = proj.blog
metadata = "" (S)
name* = "" (S)
list_posts = (LO) !proj.post
headline = "" (S)
""",
]


def parse_schema_and_id(s):
    m = re.match(SCHEME_UID_PAT, s)
    if m:
        return m.groupdict()["schema"], int(m.groupdict()["id"])
    return None, None


class BCDB(BackendMixin):
    def __init__(self, name="test"):
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.bcdb = None
        try:
            self.bcdb = j.data.bcdb.get(name=name)
        except:
            self.bcdb = j.data.bcdb.new(name=name)

        self.bcdb.reset()
        for s in schemas:
            j.data.schema.add_from_text(s)
            m = self.bcdb.model_get_from_schema(s)
            # o = m.new()
            # o.save()

    def get_schema_by_url(self, url):
        schema = j.data.schema.get_from_url_latest(url=url)
        return schema

    def get_model_by_schema_url(self, schema_url):

        return self.bcdb.model_get_from_url(schema_url)

    def get_object_by_id(self, obj_id, schema=None):
        m = self.get_model_by_schema_url(schema)
        try:
            return m.get(obj_id=obj_id)
        except:
            # import ipdb; ipdb.set_trace()
            o = m.new({"id": int(obj_id)})
            # o = m.new()
            o._model = m

            o.save()
            return o

    def recover_graph(self):
        root_objs = self.bcdb.get_all()
        graph = {}
        for root_obj in root_objs:
            soul = json.loads(getattr(root_obj, BCDBMETADATA))[SOUL]
            graph[soul] = self.recover_obj(root_obj)
        return desolve(graph)

    def recover_obj(self, root_obj):
        db_form = defaultify(root_obj._ddict)
        return self.convert_to_graph(self.parse_metadata(db_form))

    def parse_metadata(self, obj):
        if not isinstance(obj, dict):
            return obj
        result = obj.copy()
        if BCDBMETADATA in result:
            result[METADATA] = json.loads(result.pop(BCDBMETADATA))
        for k, v in result.items():
            if isinstance(v, list):
                result[k] = list(map(self.parse_metadata, v))
            else:
                result[k] = self.parse_metadata(v)
        return result

    def stringify_metadata(self, obj):
        if not isinstance(obj, dict):
            return obj
        result = obj.copy()
        for k, v in result.items():
            if isinstance(v, list):
                result[k] = list(map(self.stringify_metadata, v))
            else:
                result[k] = self.stringify_metadata(v)
        if METADATA in result:
            result[BCDBMETADATA] = json.dumps(result.pop(METADATA))
        return result

    def set_object_attr(self, obj, attr, val):
        setattr(obj, attr, val)
        return obj

    def save_object(self, obj, obj_id, schema=None):
        db_obj = self.get_object_by_id(obj_id, schema)
        obj = self.stringify_metadata(self.delegate_list_metadatata(obj))
        self.set_graph_to_obj(obj, db_obj)
        db_obj.save()
        print("obj: ", obj)

    def set_graph_to_obj(self, graph, obj):
        for k, v in graph.items():
            if isinstance(v, dict):
                self.set_graph_to_obj(v, getattr(obj, k))
            else:
                setattr(obj, k, v)

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
