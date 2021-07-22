# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from codequick import Route
from codequick.listing import Listitem

@Route.register
def watchmojo(plugin, content_type="video"):
    yield Listitem.youtube("UCaWd5_7JhbQBe4dknZhsHJg", label="WatchMojo")