# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from resources.lib.catalogo import navigation, CATALOGO_MEDIASET

from codequick import run, Route, Listitem, utils
import sys

@Route.register
def root(plugin):
    yield Listitem.from_dict(navigation, label="Catalogo", params={'id': CATALOGO_MEDIASET})
    yield Listitem.from_dict(reset, label=utils.bold("Reset"))

@Route.register
def reset(plugin):
    sys.exit()
