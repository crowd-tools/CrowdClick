import unittest

from ad_source.utils import convert_url


class ConvertUrlTestCase(unittest.TestCase):

    def test_prepend_http(self):
        self.assertEqual(
            'http://crowdholding.com',
            convert_url('crowdholding.com')
        )

    def test_prepend_http_keep_www(self):
        self.assertEqual(
            'http://www.crowdholding.com',
            convert_url('www.crowdholding.com')
        )

    def test_keep_http_schema(self):
        self.assertEqual(
            'http://crowdholding.com',
            convert_url('http://crowdholding.com')
        )

    def test_keep_https_schema(self):
        self.assertEqual(
            'https://crowdholding.com',
            convert_url('https://crowdholding.com')
        )
