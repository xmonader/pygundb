from collections import defaultdict
from .backend import BackendMixin
from pickle import loads, dumps
import os


def format_object_id(schema, id):
    return "{}://{}".format(schema, id)


class Pickle(BackendMixin):
    def __init__(self, pickledbpath="/tmp/gundb.dat"):
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.pickledbpath = pickledbpath
        self.pickledb = None
        if os.path.exists(self.pickledbpath):
            with open(self.pickledbpath, "rb") as f:
                self.pickledb = loads(f.read())
        else:
            self.pickledb = {}

    def savedb(self):
        with open(self.pickledbpath, "wb") as f:
            f.write(dumps(self.pickledb))

    def get_object_by_id(self, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        return self.pickledb.get(full_id, {"id": obj_id})

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        self.pickledb[full_id] = obj
        self.savedb()

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
