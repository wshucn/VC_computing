class Article:
    def __init__(self, url, title, update_time, content):
        self._title = title
        self._url = url
        self._update_time = update_time
        self._content = content

    @property
    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    @property
    def url(self):
        return self._url

    def set_url(self, url):
        self._url = url

    @property
    def update_time(self):
        return self._update_time

    def set_update_time(self, update_time):
        self._update_time = update_time

    @property
    def content(self):
        return self._content

    def set_content(self, content):
        self._content = content
