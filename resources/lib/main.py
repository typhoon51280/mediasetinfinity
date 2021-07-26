# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from resources.lib.catalogo import navigation, CATALOGO_MEDIASET

from codequick import Route, Resolver, Listitem, Script, run, storage, utils
from codequick.support import dispatcher
import urlquick
import xbmcgui
import sys

# Localized string Constants
SELECT_TOP = 30001
TOP_VIDEOS = 30002
PARTY_MODE = 589
FEATURED = 30005

BASE_URL = "https://www.metalvideo.com"
url_constructor = utils.urljoin_partial(BASE_URL)

@Route.register
def root(plugin):
    yield Listitem.from_dict(navigation, label="Catalogo", params={'id': CATALOGO_MEDIASET})
    yield Listitem.from_dict(reset, label=utils.bold("RESET"))

@Route.register
def reset(plugin):
    Script.log("reset", lvl=Script.INFO)
    dispatcher.reset()
    dispatcher.registered_routes = {}
    sys.exit()
