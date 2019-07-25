from collections import defaultdict
from .backend import BackendMixin

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

    def get_object_by_id(self, obj_id, schema):
        col = self.mongodb[schema]
        obj = col.find_one({"id": obj_id})
        if not obj:
            col.insert_one({"id":obj_id})
            obj = col.find_one({"id": obj_id})
        return obj

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        col = self.mongodb[schema]
        col.find_one_and_update({"id":obj_id}, {"$set": obj}, upsert=True)

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
