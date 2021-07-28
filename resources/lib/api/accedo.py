import json
import urlquick
from codequick import Route, Script, utils
from codequick.listing import Art, Info, Context, Property, Stream
from requests.auth import AuthBase
from resources.lib.six import string_types
from resources.lib.api.utils import route_callback

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

    def listItem(self, data):
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
            'callback': route_callback("catalogo", data['_meta']['attrs']['componentType']),
        }

    def component_brands(self, data):
        return {
            'label': data['title'],
            'params': {
                'uxReferenceV2': data['uxReferenceV2'] if 'uxReferenceV2' in data else None,
                'feedurlV2': data['feedurlV2'] if 'feedurlV2' in data else None,
            },
            'callback': route_callback("catalogo", data['_meta']['attrs']['componentType']),
        }

    def component_video_mixed(self, data):
        return {
            'label': data['title'],
            'params': {
                'uxReferenceV2': data['uxReferenceV2'] if 'uxReferenceV2' in data else None,
                'feedurlV2': data['feedurlV2'] if 'feedurlV2' in data else None,
            },
            'callback': route_callback("catalogo", data['_meta']['attrs']['componentType']),
        }

    def images_map(self, baseUrl, data):
        def __map(el):
            dim = el[0].split("x")
            width = float(dim[0])
            height = float(dim[1])
            ratio =  round(width/height, 2)
            return {
                'width': width,
                'height': height,
                'ratio': ratio,
                'url': el[1],
            }
        image_data = []
        for el in map(__map, data.items()):
            image_data.append({
                'width': el['width'],
                'height': el['height'],
                'ratio': el['ratio'],
                'url': baseUrl + el['url'],
            })
            image_data.append({
                'width': el['width'] * 2.0,
                'height': el['height'] * 2.0,
                'ratio': el['ratio'],
                'url': baseUrl + el['url'].replace(".jpg", "@2.jpg"),
            })
            image_data.append({
                'width': el['width'] * 3.0,
                'height': el['height'] * 3.0,
                'ratio': el['ratio'],
                'url': baseUrl + el['url'].replace(".jpg", "@3.jpg"),
            })
        return image_data

    def images_filter(self, items, ratio=0.0, wmin=0.0, hmin=0.0, wmax=0.0, hmax=0.0):
        data = filter(lambda x: x['width']>wmin and x['height']>hmin and (wmax==0 or x['width']<wmax) and (hmax==0 or x['height']<hmax), items)
        for x in data:
            x['ratio_len_0'] = round(ratio, 2)
            x['ratio_len_1'] = round(abs(x['ratio']-x['ratio_len_0']), 2)
            x['sort'] = round(abs(x['ratio']-ratio) + (10000.0-x['width'])/10000000.0, 6)
        data_sorted = sorted(data, key=lambda x: x['sort'])
        Script.log("img_data_sorted = %s", [data_sorted], Script.DEBUG)
        return data_sorted[0]

    def component_banner(self, data):
        item = self.entry(data['items'][0])
        img = json.loads(item['img'])
        images = self.images_map(img['data']['p'], img['data']['i'])
        Script.log("images = %s", [images], Script.DEBUG)
        img_poster = self.images_filter(images, 3.0/5.0)['url']
        img_fanart = self.images_filter(images, 16.0/9.0)['url']
        img_thumb = self.images_filter(images, 4.0/4.0)['url']
        return {
            'label': data['title'],
            'art': {
                'poster': img_poster,
                'banner': img_fanart,
                'fanart': img_fanart,
                'landscape': img_fanart,
                'thumb': img_thumb,
                # 'icon': self.metadata['assets']['shortLogoSecondary'].replace(".png", "@2.png"),
            },
            'info': {
                'plot': item['subtitle']
            },
            'params': {
                'uxReferenceV2': item['uxReferenceV2'] if 'uxReferenceV2' in item else None,
                'feedurlV2': item['feedurlV2'] if 'feedurlV2' in item else None,
            },
            'callback': route_callback("catalogo", data['_meta']['attrs']['componentType']),
        }
