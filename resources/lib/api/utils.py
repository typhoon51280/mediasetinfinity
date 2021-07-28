

from codequick import Route, Script

def route_callback(route, callback):
    ref = Route.ref("/resources/lib/{route}:{callback}".format(route=route, callback=callback.replace("-", "_").lower()))
    Script.log("Route [%s]", [ref.path], Script.DEBUG)
    return ref