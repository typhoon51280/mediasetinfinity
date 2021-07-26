import json

import urlquick
from codequick import Route, Script, utils
from requests.auth import AuthBase
from resources.lib.six import string_types

#: The time in seconds where a cache item is considered stale.
#: Stale items will stay in the database to allow for conditional headers.
urlquick.MAX_AGE = 60 * 60 * 4  # 4 Hours

BASE_URL = "https://api.one.accedo.tv"
APP_KEY = "6023de431de1c4001877be3b"
GID = "default"
UUID = "uuid"

url_constructor = utils.urljoin_partial(BASE_URL)

class Auth(AuthBase):
    def __init__(self):
        url = url_constructor("/session")
        response = urlquick.get(url, {'appKey': APP_KEY, 'gid': GID, 'uuid': UUID})
        self.sessionKey = response.json()['sessionKey']

    def __call__(self, r):
        r.headers['x-session'] = self.sessionKey
        return r

class ApiAccedo():

    def __init__(self):
        self._session = urlquick.session()
        self._auth = Auth()
        url = url_constructor("/metadata")
        response = self.session.get(url, auth=self.auth)
        self._metadata = response.json()

    @property
    def metadata(self):
        return self._metadata

    @property
    def auth(self):
        return self._auth

    @property
    def session(self):
        return self._session

    @property
    def availableRadios(self):
        response = self.session.get(self.metadata['mobile']['player']['radio']['feedUrl'])
        return response.json()['genres']

    def entry(self, id, locale="it"):
        url = url_constructor("/content/entry/{id}".format(id=id))
        response = self.session.get(url, params={'locale': locale}, auth=self.auth)
        return response.json()

    def entriesById(self, ids, locale="it"):
        url = url_constructor("/content/entries")
        if not isinstance(ids, string_types):
            ids = ",".join(ids)
        response = self.session.get(url, params={'locale': locale, 'id': ids}, auth=self.auth)
        return response.json()

    def entriesByAlias(self, alias, locale="it"):
        url = url_constructor("/content/entries")
        response = self.session.get(url, params={'locale': locale, 'typeAlias': alias}, auth=self.auth)
        return response.json()

    def mapItem(self, data):
        if data and '_meta' in data:
            typeAlias = data['_meta']['typeAlias']
            if typeAlias == 'navigation-item':
                return self.navigation_item(data)
            elif typeAlias == 'component-brands':
                return self.component_brands(data)
            elif typeAlias == 'component-video-mixed':
                return self.component_video_mixed(data)
            elif typeAlias == 'component-banner':
                return self.component_banner(data)
        else:
            return False

    def navigation_item(self, data):
        ctaLink = json.loads(data['ctaLink'])
        return {
            'label': data['title'],
            'params': {
                'id': ctaLink['referenceId']
            },
            'callback': self.route("catalogo", data['_meta']['attrs']['componentType']),
        }

    def component_brands(self, data):
        return {
            'label': data['title'],
            'params': {
                'uxReferenceV2': data['uxReferenceV2'] if 'uxReferenceV2' in data else None,
                'feedurlV2': data['feedurlV2'] if 'feedurlV2' in data else None,
            },
            'callback': self.route("catalogo", data['_meta']['attrs']['componentType']),
        }

    def component_video_mixed(self, data):
        return {
            'label': data['title'],
            'params': {
                'uxReferenceV2': data['uxReferenceV2'] if 'uxReferenceV2' in data else None,
                'feedurlV2': data['feedurlV2'] if 'feedurlV2' in data else None,
            },
            'callback': self.route("catalogo", data['_meta']['attrs']['componentType']),
        }
    
    def component_banner(self, data):
        item = self.entry(data['items'][0])
        return {
            'label': data['title'],
            'params': {
                'uxReferenceV2': item['uxReferenceV2'] if 'uxReferenceV2' in item else None,
                'feedurlV2': item['feedurlV2'] if 'feedurlV2' in item else None,
            },
            'callback': self.route("catalogo", data['_meta']['attrs']['componentType']),
        }

    def route(self, route, callback):
        ref = Route.ref("/resources/lib/{route}:{callback}".format(route=route, callback=callback.replace("-", "_").lower()))
        Script.log("Route [%s]", [ref.path], Script.DEBUG)
        return ref
