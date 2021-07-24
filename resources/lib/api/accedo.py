import urlquick
from codequick.utils import urljoin_partial

#: The time in seconds where a cache item is considered stale.
#: Stale items will stay in the database to allow for conditional headers.
urlquick.MAX_AGE = 60 * 60 * 4  # 4 Hours

BASE_URL = "https://api.one.accedo.tv"
url_constructor = urljoin_partial(BASE_URL)

def getSessionKey(self):
    url = url_constructor("/session")
    urlquick.get(url)