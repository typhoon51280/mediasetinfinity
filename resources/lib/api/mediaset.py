import urlquick
from uuid import uuid4
from codequick import Route, Script, utils
from codequick.listing import Art, Info, Context, Property, Stream
from requests.auth import AuthBase
from resources.lib.api.utils import route_callback

BASE_URL = "https://api-ott-prod-fe.mediaset.net/{environment}/{product}/"
url_constructor = utils.urljoin_partial(BASE_URL.format(environment="PROD", product="play"))

API_KEY = "3_l-A-KKZVONJdGd272x41mezO6AUV4mUoxOdZCMfccvEXAJa6COVXyT_tUdQI03dh"

class Auth(AuthBase):

    def __init__(self, email=None, password=None):
        Script.log("Init Auth Mediaset", lvl=Script.DEBUG)
        self._session = urlquick.session()
        self._clientId = str(uuid4())
        self._isAnonymous = not (email and password)
        if self.isAnonymous:
            self.anonymousLogin()
        else:
            self.login(email, password)
            self.accountLogin()
            self.personaSelect()

    def anonymousLogin(self):
        Script.log("anonymousLogin", lvl=Script.DEBUG)
        url = url_constructor("idm/anonymous/login/v2.0")
        response = self.session.post(url, json={
            "appName": "web/mediasetplay-web",
            "client_id": self.clientId,
        })
        Script.log("anonymousLogin response: %s", args=[response], lvl=Script.DEBUG)
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
            "id": persona['id'] if persona and 'id' in persona else self.defaultPersona['id'],
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
    def defaultPersona(self):
        return self._defaultPersona

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

    def listItem(self, data):
        if data and 'programtype' in data and data['programtype']:
            programtype = data['programtype'].lower()
            Script.log("programtype: %s", [programtype], Script.DEBUG)
            if programtype == "tvseason":
                return self.tvseason(data)
        else:
            return False

    def tvseason(self, data):
        return {
            'label': data['title'],
            'params': {
                'seriesId': data['seriesId'] if 'seriesId' in data else None,
                'seasonId': data['id'] if 'id' in data else None,
            },
            'callback': route_callback("catalogo", "tvseason"),
        }