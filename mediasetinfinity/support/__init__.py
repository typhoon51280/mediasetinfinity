from __future__ import unicode_literals, absolute_import
from mediasetinfinity.support.routing import CallbackRef, run
from mediasetinfinity.support.monkey import patch
import xbmc

KODI_VERSION_MAJOR = int(xbmc.getInfoLabel('System.BuildVersion').split('.')[0])

patch(CallbackRef)

__all__ = [
    "run",
]