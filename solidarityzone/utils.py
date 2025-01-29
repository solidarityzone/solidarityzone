from itertools import groupby
from operator import itemgetter


# Helper method to group an array by values
def group_by(arr, key):
    return [[x for x in g] for k, g in groupby(arr, key=itemgetter(key))]


# Helper method to insert key in a certain position in a dict
def insert_into_dict(existing, pos, key, value):
    keys = list(existing.keys())
    if key in existing:
        existing[key].append(value)
        return existing
    else:
        keys.insert(pos, key)
        return {k: existing.get(k, [value]) for k in keys}


def list_to_str(lst: list):
    s = ""
    for i in lst:
        s += chr(i + ord("0"))
    return s
