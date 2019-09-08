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

class Memory(BackendMixin):
    def __init__(self):
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.objs = defaultdict(lambda: cuteobj())

    def get_object_by_id(self, obj_id, schema=None):
        return self.objs.get(obj_id, {})

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        self.objs[obj_id] = obj

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
