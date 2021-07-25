import json

import urlquick
from codequick import Route
from codequick.utils import urljoin_partial
from requests.auth import AuthBase
from resources.lib.six import string_types

#: The time in seconds where a cache item is considered stale.
#: Stale items will stay in the database to allow for conditional headers.
urlquick.MAX_AGE = 60 * 60 * 4  # 4 Hours

BASE_URL = "https://api.one.accedo.tv"
APP_KEY = "6023de431de1c4001877be3b"
GID = "default"
UUID = "uuid"

url_constructor = urljoin_partial(BASE_URL)


class Auth(AuthBase):
    def __init__(self):
        url = url_constructor("/session")
        response = urlquick.get(
            url, {'appKey': APP_KEY, 'gid': GID, 'uuid': UUID})
        self.sessionKey = response.json()['sessionKey']

    def __call__(self, r):
        r.headers['x-session'] = self.sessionKey
        return r


class ApiAccedo():

    def metadata(self):
        url = url_constructor("/metadata")
        response = urlquick.get(url, auth=Auth())
        self.metadata = response.json()
        return self.metadata

    def entry(self, id, locale="it"):
        url = url_constructor("/content/entry/{id}".format(id=id))
        response = urlquick.get(url, params={'locale': locale}, auth=Auth())
        return response.json()

    def entriesById(self, ids, locale="it"):
        url = url_constructor("/content/entries")
        if not isinstance(ids, string_types):
            ids = ",".join(ids)
        response = urlquick.get(
            url, params={'locale': locale, 'id': ids}, auth=Auth())
        return response.json()

    def entriesByAlias(self, alias, locale="it"):
        url = url_constructor("/content/entries")
        response = urlquick.get(
            url, params={'locale': locale, 'typeAlias': alias}, auth=Auth())
        return response.json()

    def availableRadios(self):
        response = urlquick.get(
            "https://api.cloud.mediaset.net/api/available-radios")
        return response.json()['genres']

    def mapItem(self, data):
        if data and '_meta' in data:
            typeAlias = data['_meta']['typeAlias']
            if typeAlias == 'navigation-item':
                return self.navigation_item(data)
            elif typeAlias == 'component-brands':
                return self.component_brands(data)
            elif typeAlias == 'component-video-mixed':
                return self.listingPage(data)
        else:
            return None

    def navigation_item(self, data):
        ctaLink = json.loads(data['ctaLink'])
        return {
            'label': data['title'],
            'params': {'id': ctaLink['referenceId']},
            'callback': self.route("catalogo", ctaLink['referenceType'])
        }

    def component_brands(self, data):
        return {
            'label': data['title'],
            'params': {'uxReferenceV2': data['uxReferenceV2']},
            'callback': self.route("catalogo", data['_meta']['attrs']['componentType'])
        }

    def component_video_mixed(self, data):
        return {
            'label': data['title'],
            'params': {'feedurlV2': data['feedurlV2']},
            'callback': self.route("catalogo", data['_meta']['attrs']['componentType'])
        }

    def route(self, route, callback):
        return Route.ref("/resources/lib/{route}:{callback}".format(route, callback.replace("-","_")))
