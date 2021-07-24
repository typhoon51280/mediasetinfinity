# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from codequick import Route
from codequick.listing import Listitem

@Route.register
def catalogoMPI(plugin):
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")

@Route.register
def sections(plugin):
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")
    yield Listitem.from_dict(programmi_tv, label="Programmi Tv")


@Route.register
def programmi_tv(plugin):
    yield Listitem.from_dict("/resources/lib/catalogo:sections", label="Catalogo")