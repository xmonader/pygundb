from collections import defaultdict
from .backend import BackendMixin
from .utils import defaultify
from .resolvers import desolve


class cuteobj:
    def __getattr__(self, attr):
        if attr in dir(self):
            return getattr(self, attr)
        else:
            setattr(self, attr, cuteobj())

    def __str__(self):
        return "cuteobj: {} ".format(str(self.__dict__))

class Mongo(BackendMixin):
    def __init__(self, connstring='mongodb://localhost:27017'):
        from pymongo import MongoClient
        self.cl = MongoClient(connstring)
        self.mongodb = self.cl.test_database
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.cache = {}

    def get_object_by_id(self, obj_id, schema):
        col = self.mongodb[schema]
        obj = col.find_one({"id": obj_id})
        if not obj:
            col.insert_one({"id": obj_id})
            obj = col.find_one({"id": obj_id})
        del obj['_id']
        return defaultify(obj)

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        col = self.mongodb[schema]
        obj = self.delegate_list_metadatata(obj)
        col.find_one_and_update({"id":obj_id}, {"$set": obj}, upsert=True)

    def recover_graph(self):
        schmeas = self.mongodb.list_collection_names()
        graph = {}
        for schema in schmeas:
            for obj in self.mongodb[schema].find({}):
                full_schema_id = schema + "://" + str(obj['id'])
                del obj['_id']
                graph[full_schema_id] = self.convert_to_graph(obj)
        return desolve(graph)

    def recover_obj(self, key):
        db_form = defaultify(json.loads(self.redis.get(key)))
        return self.convert_to_graph(db_form)
    

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
