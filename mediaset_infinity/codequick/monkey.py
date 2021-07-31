
from codequick.support import CallbackRef

def PatchCallbackRef(cls):
    def __json__(self):
        return self.path
    cls.__json__ = __json__


def patch(cls):
    if type(cls)==type(CallbackRef):
        PatchCallbackRef(cls)