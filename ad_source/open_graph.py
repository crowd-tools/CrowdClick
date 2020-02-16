from opengraph import OpenGraph


class CustomOpenGraph(OpenGraph):

    def __init__(self, url=None, html=None, useragent=None):
        self.__data__ = {}
        super().__init__(url=url, html=html, useragent=useragent)
