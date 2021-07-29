

from typing import Iterable
from codequick import Route, Script
from resources.lib.six import string_types

def route_callback(route, callback):
    ref = Route.ref("/resources/lib/{route}:{callback}".format(route=route, callback=callback.replace("-", "_").lower()))
    Script.log("Route [%s]", [ref.path], Script.DEBUG)
    return ref

def string_join(ids, separator=","):
    if isinstance(ids, string_types):
        return ids
    elif isinstance(ids, Iterable[str]):
        return separator.join(ids)
    else:
        return ""