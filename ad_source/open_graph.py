import re

import requests
from bs4 import BeautifulSoup


class OpenGraph(object):
    ILEGAL_FRAME_OPTIONS = frozenset(['deny', 'sameorigin'])
    X_FRAME_OPTIONS = None  # None, `deny`, `sameorigin` or `allow-from X`
    RESOLVED_URL = None

    def __init__(self, url=None):
        self.og_data = {}
        content, allow_iframe_option = self._fetch(url)
        self.X_FRAME_OPTIONS = allow_iframe_option
        self._parse(content)

    def __getattr__(self, name):
        return self.og_data.get(name)

    def _fetch(self, url) -> tuple:
        """
        :param url: URL to fetch
        :return: 'Response body' and 'X-Frame-Options' header
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        }
        self.response = requests.get(url, allow_redirects=True, headers=headers)
        self.RESOLVED_URL = self.response.url
        x_frame_options = self.response.headers.get('X-Frame-Options', '').lower()
        if x_frame_options in self.ILEGAL_FRAME_OPTIONS or x_frame_options.startswith('allow-from'):
            # XXX Allow-from <us>
            return self.response.text, x_frame_options
        return self.response.text, None

    def _parse(self, html):
        doc = BeautifulSoup(html, features="html.parser")
        ogs = doc.html.head.findAll(property=re.compile(r'^og'))

        for og in ogs:
            if og.has_attr('content'):
                self.og_data[og['property'][3:]] = og['content']
