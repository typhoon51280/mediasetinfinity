# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from mediasetinfinity.api import ApiMediaset, ApiAccedo, ApiComcast
from mediasetinfinity.support import strings, logger
from mediasetinfinity.support.routing import Route, Resolver, Listitem
from itertools import chain

CATALOGO_MEDIASET = "600af5c21de1c4001bfadf4f"
ROUTE = "catalogo"

def listItems(data, mapItem, **kwargs):
    no_data = True
    if data:
        for item in data:
            if item:
                logger.debug("[item] %s", strings.tojson(item))
                listItem = mapItem(item, **kwargs)
                logger.debug("[listItem] %s", strings.tojson(listItem))
                if listItem:
                    no_data = False
                    yield Listitem.from_dict(**listItem)
    if no_data:
        yield False

@Route.register(content_type=None)
def navigation(plugin, id=CATALOGO_MEDIASET):
    apiAccedo = ApiAccedo()
    navItems = apiAccedo.entry(id)['navItems']
    logger.debug("[navItems] %s", navItems)
    data = apiAccedo.entriesById(navItems)
    # logger.debug("[data] %s", data)
    return listItems(data['entries'], apiAccedo.listItem)

@Route.register(content_type=None)
def navitem(plugin, id):
    apiAccedo = ApiAccedo()
    components = apiAccedo.entry(id)['components']
    logger.debug("[components] %s", components)
    data = apiAccedo.entriesById(components)
    # logger.debug("[data] %s", data)
    return listItems(data['entries'], apiAccedo.listItem)

@Route.register(content_type=None)
def banner(plugin, uxReferenceV2, feedurlV2):
    yield False

@Route.register(content_type=None)
def brands(plugin, uxReferenceV2, feedurlV2):
    if uxReferenceV2:
        apiMediaset = ApiMediaset()
        data = apiMediaset.reco(uxReference=uxReferenceV2)
        logger.debug("[data] %s", data)
        return listItems(data['entries'], apiMediaset.listItem)
    elif feedurlV2:
        apiComcast = ApiComcast()
        data = apiComcast.feeds(feedurlV2)
        return listItems(data['entries'], apiComcast.listItem)
    return False

@Route.register(content_type=None)
def tvserie(plugin, seriesGuid, seriesId):
    apiComcast = ApiComcast()
    data_series = apiComcast.seriesByGuid(seriesGuid)
    if data_series and 'entries' in data_series and data_series['entries']:
        data_serie = data_series['entries'][0]
        seriesTvSeasons = list(map(lambda x: apiComcast.tvSeasonByGuid(x['guid'])['entries'][0] if 'guid' in x else None, sorted(filter(lambda x: x['id'] in data_serie['availableTvSeasonIds'] , data_serie['seriesTvSeasons']), key=lambda x: x['tvSeasonNumber'])))
        return listItems(seriesTvSeasons, apiComcast.listItem, apitype=data_serie['apitype'], datatype="mediasettvseason")
    return False

@Route.register(content_type=None)
def tvseason(plugin, seriesGuid, seasonGuid, seriesId, seasonId):
    apiComcast = ApiComcast()
    subbrands = apiComcast.subbrandByTvSeasonId(seasonId)
    if subbrands and 'entries' in subbrands and subbrands['entries']:
        data_subbrands = subbrands['entries']
        return listItems(data_subbrands, apiComcast.listItem, apitype=subbrands['apitype'], datatype=subbrands['datatype'], programtype="subbrand")
    return False

@Route.register(content_type=None)
def subbrand(plugin, subBrandId, seriesId, tvSeasonId):
    apiComcast = ApiComcast()
    programs = apiComcast.subBrandHomeMethod(subBrandId)
    logger.debug("[programs] %s", programs)
    if programs and 'entries' in programs and programs['entries']:
        data_programs = programs['entries']
        logger.debug("[data_programs] %s", data_programs)
        return listItems(data_programs, apiComcast.listItem, datatype="mediasetprogram")
    return False

@Resolver.register()
def play(plugin, guid):
    apiMediaset =  ApiMediaset()
    program = apiMediaset.check(guid)
    logger.debug("[program] %s", program)
    logger.debug("[media] %s", program['media'])
    if program and 'media' in program:
        video = apiMediaset.getVideo(program['media'])
        logger.debug("[video] %s", video)
        if video:
            mapItem = apiMediaset.listItem(video, programtype="vod")
            logger.debug("[mapItem] %s", mapItem)
            if mapItem:
                item = Listitem.from_dict(**mapItem)
                item.listitem.setMimeType(video['type'])
                item.listitem.setContentLookup(False)
                listitem = item.build()[1]
                logger.debug("[path] %s", listitem.getPath())
                logger.debug("[folder] %s", listitem.getProperty("folder"))
                logger.debug("[isplayable] %s", listitem.getProperty("isplayable"))
                logger.debug("[mediatype] %s", listitem.getVideoInfoTag().getMediaType())
                return listitem
    return False
