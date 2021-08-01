# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from mediasetinfinity.routes.catalogo import navigation, CATALOGO_MEDIASET
from mediasetinfinity.support.routing import Route, Listitem, Script, dispatcher
import sys
import xbmc

@Route.register
def root(plugin):
    yield Listitem.from_dict(navigation, label="Catalogo", params={'id': CATALOGO_MEDIASET})
    yield Listitem.from_dict(reset, label="Reset") # FOR RAPID DEVELOPMENT

@Route.register
def reset(plugin):
    dispatcher.reset()
    dispatcher.registered_routes = {}
    sys.exit()
