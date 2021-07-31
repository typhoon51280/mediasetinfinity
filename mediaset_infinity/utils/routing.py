from codequick import Route
from itertools import chain

def route_callback(route, callback):
    ref = Route.ref("/mediaset_infinity/routes/{route}:{callback}".format(route=route, callback=callback.replace("-", "_").lower()))
    return ref

def generators(*args):
    return chain(args)