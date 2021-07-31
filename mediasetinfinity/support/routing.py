from __future__ import absolute_import

from codequick import Route, Script
from itertools import chain

def route_callback(route, callback):
    ref = Route.ref("/mediasetinfinity/routes/{route}:{callback}".format(route=route, callback=callback.replace("-", "_").lower()))
    return ref
