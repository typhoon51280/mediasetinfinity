from __future__ import absolute_import
from codequick import utils as utils, storage as storage, Route, Resolver, Listitem, Script
from codequick.support import CallbackRef, run, logger_id, dispatcher
from codequick.script import addon_logger

def callback(route, callback):
    ref = Route.ref("/mediasetinfinity/routes/{route}:{callback}".format(route=route, callback=callback.replace("-", "_").lower()))
    return ref
