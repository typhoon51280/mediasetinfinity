from __future__ import unicode_literals, absolute_import
from mediasetinfinity.support.routing import CallbackRef, run
from mediasetinfinity.support.monkey import patch

patch(CallbackRef)

__all__ = [
    "run",
]