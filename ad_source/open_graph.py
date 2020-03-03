import re

import requests
from bs4 import BeautifulSoup


class OpenGraph(object):

    def __init__(self, url):
        self.og_data = {}
        content = self._fetch(url)
        self._parse(content)

    def __contains__(self, item):
        return item in self.og_data

    def __getattr__(self, name):
        return self.og_data.get(name)

    def __repr__(self):
        return self.og_data.__str__()

    def __str__(self):
        return self.__repr__()

    def _fetch(self, url):
        response = requests.get(url, allow_redirects=True)
        return response.text

    def _parse(self, html):
        doc = BeautifulSoup(html, features="html.parser")
        ogs = doc.html.head.findAll(property=re.compile(r'^og'))

        for og in ogs:
            if og.has_attr('content'):
                self.og_data[og['property'][3:].lower()] = og['content']
