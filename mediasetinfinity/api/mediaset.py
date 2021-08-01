from __future__ import unicode_literals, absolute_import
import json
import urlquick
from uuid import uuid4
from requests.auth import AuthBase
from mediasetinfinity.support import logger, KODI_VERSION_MAJOR
from mediasetinfinity.support.routing import utils, callback

BASE_URL = "https://api-ott-prod-fe.mediaset.net/{environment}/{product}/"
url_constructor = utils.urljoin_partial(BASE_URL.format(environment="PROD", product="play"))

API_KEY = "3_l-A-KKZVONJdGd272x41mezO6AUV4mUoxOdZCMfccvEXAJa6COVXyT_tUdQI03dh"
WIDEVINE_URL = "https://widevine.entitlement.theplatform.eu/wv/web/ModularDrm/getRawWidevineLicense"
ACCOUNT_ID = "http://access.auth.theplatform.com/data/Account/2702976343"

class Auth(AuthBase):

    def __init__(self, username=None, password=None):
        logger.debug("Init Auth Mediaset")
        self._session = urlquick.session()
        self._clientId = str(uuid4())
        self._isAnonymous = not (username and password)
        if self.isAnonymous:
            self.anonymousLogin()
        else:
            self.login(username, password)
            self.accountLogin()
            self.personaSelect()

    def anonymousLogin(self):
        logger.debug("anonymousLogin")
        url = url_constructor("idm/anonymous/login/v2.0")
        response = self.session.post(url, json={
            "appName": "web/mediasetplay-web",
            "client_id": self.clientId,
        })
        logger.debug("anonymousLogin response: %s", response)
        if response.status_code == 200:
            jsn = response.json()
            if jsn and 'isOk' in jsn and jsn['isOk']:
                data = jsn['response']
                self._beToken = data['beToken']
                self._sid = data['sid']

    def login(self, username, password):
        url = "https://login.mediaset.it/accounts.login"
        response = self.session.post(url, data={
            "APIKey": API_KEY,
            "loginID": username,
            "password": password,
            "sessionExpiration": 31536000,
            "include": "profile,data,emails,subscriptions,preferences,id_token,data.fastLoginPIN",
            "includeUserInfo": "true",
            "authMode": "cookie",
            "format": "json",
        })
        if response.status_code == 200:
            jsn = response.json()
            if jsn and 'errorCode' in jsn and jsn['errorCode']==0:
                self._idToken = jsn['id_token']

    def accountLogin(self):
        url = url_constructor("idm/account/login/v2.0")
        response = self.session.post(url, json={
            "appName": "web/mediasetplay-web",
            "gt": self.idToken,
            "client_id": self.clientId,
            "include": "personas,adminBeToken",
        })
        if response.status_code == 200:
            jsn = response.json()
            if jsn and 'isOk' in jsn and jsn['isOk']:
                data = jsn['response']
                self._sid = data['sid']
                self._caToken = data['caToken']
                self._adminBeToken = data['adminBeToken']
                self._account = data['account']

    def personaSelect(self, persona=None):
        url = url_constructor("idm/persona/login/v2.0")
        if not persona:
            for p in self.account['personas']:
                if p['id'] == self.account['accountSettings']['default']:
                    persona = p
                    break
        response = self.session.post(url, params={'sid': self.sid}, json={
            "caToken": self.caToken,
            "id": persona['id'] if persona and 'id' in persona else "",
        })
        if response.status_code == 200:
            jsn = response.json()
            if jsn and 'isOk' in jsn and jsn['isOk']:
                data = jsn['response']
                self._beToken = data['beToken']
                self._persona = persona

    @property
    def isAnonymous(self):
        return self._isAnonymous

    @property
    def session(self):
        return self._session

    @property
    def clientId(self):
        return self._clientId

    @property
    def idToken(self):
        return self._idToken

    @property
    def sid(self):
        return self._sid

    @property
    def caToken(self):
        return self._caToken

    @property
    def adminBeToken(self):
        return self._adminBeToken

    @property
    def beToken(self):
        return self._beToken

    @property
    def account(self):
        return self._account

    @property
    def persona(self):
        return self._persona

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer {beToken}".format(beToken=self.beToken)
        r.headers['User-Agent'] = "Chrome"
        return r


class ApiMediaset():

    def __init__(self, username=None, password=None):
        self._session = urlquick.session()
        self._auth = Auth(username, password)

    @property
    def auth(self):
        return self._auth

    @property
    def session(self):
        return self._session

    def reco(self, uxReference="", query="", params="", contentId="", page_number=1, page_size=50):
        if self.auth.isAnonymous:
            account_type = "anonymous"
            query_params = {
                'uxReference': uxReference,
                'query': query,
                'params': params,
                'contentId': contentId,
                'deviceId': self.auth.clientId,
                'sessionId': self.auth.sid,
                'sid': self.auth.sid,
                'property': "play",
                'tenant': "play-prod-v2",
                'hitsPerPage': page_size,
                'page': page_number,
            }
        else:
            account_type = "account"
            query_params = {
                'uxReference': uxReference,
                'query': query,
                'params': params,
                'contentId': contentId,
                'userId': self.auth.account['name'],
                'personaShortId': self.auth.persona['shortId'],
                'deviceId': self.auth.clientId,
                'sessionId': self.auth.sid,
                'sid': self.auth.sid,
                'property': "play",
                'tenant': "play-prod-v2",
                'hitsPerPage': page_size,
                'page': page_number,
            }
        url = url_constructor("reco/{account_type}/v2.0".format(account_type=account_type))
        response = self.session.get(url, params=query_params, auth=self.auth)
        if response.status_code == 200:
            jsn = response.json()
            if jsn and 'isOk' in jsn and jsn['isOk']:
                data = jsn['response']
                return {
                    'entries': data['blocks'][0]['items'],
                    'pagination': data['pagination'],
                }
        return False

    def check(self, guid, streamType=None, delivery=None):
        url = url_constructor("playback/check/v2.0")
        response = self.session.post(url, auth=self.auth, json={
            'contentId': guid,
            'streamType': streamType or "VOD",
            'delivery': delivery or "Streaming",
            'createDevice': True,
        })
        if response.status_code == 200:
            jsn = response.json()
            if jsn and 'isOk' in jsn and jsn['isOk']:
                data = jsn['response']
                logger.debug("[data] %s", data)
                return {
                    'media': data['mediaSelector'] if 'mediaSelector' in data else "",
                    'channelsRights': data['channelsRights'] if 'channelsRights' in data else "",
                    "channelsRightsUser": data['channelsRightsUser'] if 'channelsRightsUser' in data else "",
                }
        return False
    
    def getVideo(self, media, delivery=None):
        response = self.session.get(media['url'], params={
            'auth': self.auth.beToken,
            'format': media['format'],
            'formats': media['formats'],
            'assetTypes': media['assetTypes'],
            'balance': media['balance'],
            'auto': media['auto'],
            'tracking': media['tracking'],
            'delivery': delivery or "Streaming",
        })
        body = response.parse("body")
        for el in body.iterfind(".//switch"):
            vid = el.find("./video")
            ref = el.find("./ref")
            if vid is not None and ref is not None:
                security = ref.get("security", "")
                trackingData = ref.find("./param[@name='trackingData']")
                trackingDataParams = utils.parse_qs(trackingData.get("value", "").replace("|","&")) if trackingData is not None else None
                pid = trackingDataParams['pid'] if trackingDataParams and 'pid' in trackingDataParams else ""
                return {
                    'url': vid.get("src", ""),
                    'type': ref.get("type", ""),
                    'security': security == "commonEncryption",
                    'pid': pid,
                }
        return False
    
    def getLicenseKey(self, releasePid, headers=None):
        headerStr = utils.urlparse.urlencode(headers) if headers else ""
        return (
            "{url}"
            "?releasePid={releasePid}"
            "&token={token}"
            "&account={account}"
            "&schema=1.0"
            "|{headers}|R{{SSM}}|"
        ).format(url=WIDEVINE_URL, releasePid=releasePid, token=self.auth.beToken, account=ACCOUNT_ID, headers=headerStr)

    def listItem(self, data, **kwargs):
        programtype = data['programtype'].lower() if 'programtype' in data and data['programtype'] else None
        if not programtype:
            programtype = data['programType'].lower() if 'programType' in data and data['programType'] else None
        if not programtype:
            programtype = kwargs['programtype'] if 'programtype' in kwargs else None
        logger.debug("programtype: %s", programtype)
        if programtype:
            if programtype == "tvseason":
                return self.__tvseason(data)
            elif programtype == "vod":
                return self.__vod(data)
        else:
            return False

    def __vod(self, data):
        from inputstreamhelper import Helper
        is_helper = Helper("mpd", drm="com.widevine.alpha")
        if is_helper.check_inputstream():
            properties = {
                'inputstream.adaptive.manifest_type': "",
                'inputstream.adaptive.license_type': "",
                'inputstream.adaptive.license_key': "",
            }
            if KODI_VERSION_MAJOR >= 19:
                properties['inputstream'] = is_helper.inputstream_addon
            else:
                properties['inputstreamaddon'] = is_helper.inputstream_addon
            return {
                'callback': str(data['url']),
                'label': str(data['url']),
                'properties': properties,
            }
        return False

    def __tvseason(self, data):
        return {
            'label': data['title'],
            'params': {
                'seriesId': data['seriesId'] if 'seriesId' in data else None,
                'seasonId': data['id'] if 'id' in data else None,
                'seriesGuid': data['id_series_se'] if 'id_series_se' in data else None,
                'seasonGuid': data['id_series_st'] if 'id_series_st' in data else None,
            },
            'callback': callback("catalogo", "tvseason"),
        }