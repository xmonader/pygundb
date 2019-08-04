from collections import defaultdict
from ..consts import METADATA, SOUL


def uniquify(lst):
    """
    Return a list of unique items from lst.
    """
    res = []
    for item in lst:
        if not item in res:
            res.append(item)
    return res


def fix_lists(obj):
    """
    If obj is of any type other than dict, return it as is.
    Otherwise, recursively convert each entry whose key starts with list_ into a list of unique values extracted from v.values()
    """
    if not isinstance(obj, dict):
        return obj
    res = {}
    for k, v in obj.items():
        if k.startswith('list_'):
            res[k] = listify(fix_lists(v))
        else:
            res[k] = fix_lists(v)
    return res


def listify(attr):
    """
    If attr is a dict return its values as a list after eliminating duplicates in it.
    Otherwise, return its value as is.
    """
    if isinstance(attr, dict):
        return eliminate_nones(uniquify(fix_lists(attr).values()))
    else:
        return attr


def get_first_list_prop(lst):
    """
    Returns the first element in the list that starts with list_, -1 if not found.

    Arguments:
        lst {list}
    """
    for i, e in enumerate(lst):
        if e.startswith('list_'):
            return i
    return -1


rec_dd = lambda: defaultdict(rec_dd)


def defaultify(d):
    "Converts a dict to a nested default dicts"
    res = defaultdict(rec_dd)
    for k, v in d.items():
        if isinstance(v, dict):
            res[k] = defaultify(v)
        else:
            res[k] = v
    return res


def eliminate_nones(lst):
    "Removes all Nonees in the given list"
    return [x for x in lst if x is not None]


def desolve_obj(obj):
    """Returns the given object in gundb form along with the souls it created"""
    result = defaultify({})
    added_souls = defaultify({})
    for k, v in obj.items():
        if k != METADATA and isinstance(v, dict):
            prop_soul = v[METADATA][SOUL]
            result[k] = {SOUL: prop_soul}
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
