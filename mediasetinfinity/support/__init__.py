from __future__ import unicode_literals, absolute_import

from codequick.support import CallbackRef
from mediasetinfinity.support.monkey import patch
from codequick import run as start

patch(CallbackRef)

__all__ = [
    "start"
]