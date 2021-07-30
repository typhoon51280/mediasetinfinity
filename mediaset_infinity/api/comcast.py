import urlquick
from codequick import Route, Script, utils
from mediaset_infinity.utils import route_callback, string_join

BASE_URL = "https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/"
url_constructor = utils.urljoin_partial(BASE_URL)

DEFAULT_PAGE_SIZE = 50

class ApiComcast():

    def __init__(self, page_size=DEFAULT_PAGE_SIZE):
        self._page_size = page_size
        self._session = urlquick.session()

    @property
    def session(self):
        return self._session

    @property
    def page_size(self):
        return self._page_size

    ### TV SERIE ###
    def seriesByGuid(self, guid):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-series-v2"), params={
                'byGuid': guid,
            }), "series")
    ### TV SERIE ###

    ### TV SEASON ###
    def tvSeasonByGuid(self, guid):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-tv-seasons-v2"), params={
                'byGuid': guid,
            }), "tvseasons")

    def tvSeasonsEndpointMethod(self, seriesId, sort="tvSeasonNumber|asc", page_number=None, page_size=None):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-tv-seasons-v2"), params={
                'bySeriesId': seriesId,
                'sort': sort,
                'range': self.range(page_number, page_size),
            }), "tvseasons")
    
    def tvSeasonByBrandId(self, brandId):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-tv-seasons-v2"), params={
                'byCustomValue': string_join(brandId),
            }), "tvseasons")
    ### TV SEASON ###

    ### SUBBRAND ###
    def subbrandByTvSeasonId(self, tvSeasonId, sort="mediasetprogram$order"):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-subbrands-v2"), params={
                'byTvSeasonId': tvSeasonId,
                'sort': sort,
            }), "subbrands")

    def subbrandById(self, subBrandId):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-subbrands-v2"), params={
                'byCustomValue': "{{subBrandId}}{subBrandId}".format(subBrandId=subBrandId),
            }), "subbrands")
    
    def subbrandByParentId(self, parentId):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-subbrands-v2"), params={
                'byTags': "parentId:{parentId}".format(parentId=parentId),
            }), "subbrands")
    ### SUBBRAND ###

    ### EPISODE ###
    def defaultEpisodePerSeasonEndpoint(self, tvSeasonId, sort=":publishInfo_lastPublished|asc,tvSeasonEpisodeNumber|asc"):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-programs-v2"), params={
                'byTvSeasonId': tvSeasonId,
                'byCustomValue': "{editorialType}{Full Episode}",
                'sort': sort,
                'range': "1-1",
            }), "programs")

    def subBrandHomeMethod(self, subBrandId, sort=":publishInfo_lastPublished|desc,tvSeasonEpisodeNumber|desc", page_number=None, page_size=None):
        return self.__handleResponse(
            self.session.get(url_constructor("mediaset-prod-all-programs-v2"), params={
                'byCustomValue': "{{subBrandId}}{subBrandId}".format(subBrandId=subBrandId),
                'sort': sort,
                'range': self.range(page_number, page_size),
            }), "programs")
    ### EPISODE ###

    def range(self, page_number=1, page_size=None):
        if not page_size:
            page_size = self.page_size
        range_end = page_number * page_size
        range_start = range_end - page_size + 1
        return "{}-{}".format(range_start, range_end)

    def pagination(self, data):
        return {
            'page': (data['startIndex'] - 1) / data['itemsPerPage'] + 1,
            'hitsPerPage': data['itemsPerPage'],
            'hasNextPage': data['entryCount'] and data['itemsPerPage'] == data['entryCount'],
        }

    def __handleResponse(self, response, apitype=""):
        if response.status_code == 200:
            jsn = response.json()
            if 'entries' in jsn and jsn['entries']:
                return {
                    'entries': jsn['entries'],
                    'pagination': self.pagination(jsn),
                    'datatype': list(jsn['$xmlns'].keys())[0],
                    'apitype': apitype,
                }
        return False
