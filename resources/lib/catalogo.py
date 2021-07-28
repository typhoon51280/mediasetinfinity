# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from resources.lib.api.mediaset import ApiMediaset

from resources.lib.api.accedo import ApiAccedo
from codequick import Route, Listitem

CATALOGO_MEDIASET = "600af5c21de1c4001bfadf4f"

@Route.register(content_type=None)
def navigation(plugin, id=CATALOGO_MEDIASET):
    plugin.log("Route catalog:navigation %s", [id], plugin.INFO)
    apiAccedo = ApiAccedo()
    navItems = apiAccedo.entry(id)['navItems']
    plugin.log("navItems %s", [navItems], plugin.INFO)
    data = apiAccedo.entriesById(navItems)
    plugin.log("data %s", [data], plugin.DEBUG)
    no_data = True
    for item in data['entries']:
        if item:
            plugin.log("item %s", [item], plugin.DEBUG)
            listItem = apiAccedo.listItem(item)
            plugin.log("listItem %s", [listItem], plugin.DEBUG)
            if listItem:
                no_data = False
                yield Listitem.from_dict(**listItem)
    if no_data:
        yield False

@Route.register(content_type=None)
def navitem(plugin, id):
    plugin.log("Route catalog:navitem %s", [id], plugin.INFO)
    apiAccedo = ApiAccedo()
    components = apiAccedo.entry(id)['components']
    plugin.log("components %s", [components], plugin.DEBUG)
    data = apiAccedo.entriesById(components)
    plugin.log("data %s", [data], plugin.DEBUG)
    no_data = True
    for item in data['entries']:
        if item:
            plugin.log("item %s", [item], plugin.DEBUG)
            listItem = apiAccedo.listItem(item)
            plugin.log("listItem %s", [listItem], plugin.DEBUG)
            if listItem:
                no_data = False
                yield Listitem.from_dict(**listItem)
    if no_data:
        yield False

@Route.register(content_type=None)
def banner(plugin, uxReferenceV2, feedurlV2):
    plugin.log("Route catalog:banner [%s, %s]", [uxReferenceV2, feedurlV2], plugin.INFO)
    yield False

@Route.register(content_type=None)
def brands(plugin, uxReferenceV2, feedurlV2):
    plugin.log("Route catalog:brands [%s, %s]", [uxReferenceV2, feedurlV2], plugin.INFO)
    apiMediaset = ApiMediaset()
    no_data = True
    if uxReferenceV2:
        data = apiMediaset.reco(uxReference=uxReferenceV2)
        plugin.log("data [%s]", [data], plugin.DEBUG)
        for item in data['items']:
            plugin.log("item [%s]", [item], plugin.DEBUG)
            listItem = apiMediaset.listItem(item)
            plugin.log("listItem [%s]", [listItem], plugin.DEBUG)
            if listItem:
                no_data = False
                yield Listitem.from_dict(**listItem)
    if no_data:
        yield False

@Route.register(content_type=None)
def tvseason(plugin, seriesId, seasonId):
    plugin.log("Route catalog:tvseason [%s, %s]", [seriesId, seasonId], plugin.INFO)
    yield False
