import urlquick

class ApiComcast():

    def __init__(self, username=None, password=None):
        self._session = urlquick.session()
