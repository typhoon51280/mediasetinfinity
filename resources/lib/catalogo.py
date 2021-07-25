# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from resources.lib.api.accedo import ApiAccedo
from codequick import Route
from codequick.listing import Listitem
from codequick.support import logger_id

# Logger specific to this module
logger = logging.getLogger("%s.catalogo" % logger_id)

@Route.register
def navigation(plugin, id):
    apiAccedo = ApiAccedo()
    navItems = apiAccedo.entry(id)['navItems']
    logger.debug("navItems %s" % navItems)
    data = apiAccedo.entriesById(navItems)
    logger.debug("data %s" % data)
    for item in data['entries']:
        logger.debug("item %s" % item)
        if item:
            mappedItem = apiAccedo.mapItem(item)
            logger.debug("mappedItem %s" % mappedItem)
            if mappedItem:
                yield Listitem.from_dict(**mappedItem)

@Route.register
def browsepage(plugin, id):
    logger.debug("browsepage %s" % id)
    apiAccedo = ApiAccedo()
    components = apiAccedo.entry(id)['components']
    logger.debug("components %s" % components)
    data = apiAccedo.entriesById(components)
    logger.debug("data %s" % data)
    for item in data['entries']:
        logger.debug("item %s" % item)
        if item:
            mappedItem = apiAccedo.mapItem(item)
            logger.debug("mappedItem %s" % mappedItem)
            if mappedItem:
                yield Listitem.from_dict(**mappedItem)
