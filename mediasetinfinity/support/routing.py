from __future__ import absolute_import
from codequick import utils, storage, Route, Listitem, Script
from codequick.support import CallbackRef, run

def callback(route, callback):
    ref = Route.ref("/mediasetinfinity/routes/{route}:{callback}".format(route=route, callback=callback.replace("-", "_").lower()))
    return ref
