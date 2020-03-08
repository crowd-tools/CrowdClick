from urllib.parse import urlparse, ParseResult

from web3 import Web3


def to_32byte_hex(val):
    return Web3.toHex(Web3.toBytes(val).rjust(32, b'\0'))


def sig_to_vrs(sig):
    r = int(sig[2:66], 16)
    s = int(sig[66:130], 16)
    v = int(sig[130:], 16)
    return v, r, s


def convert_url(website_link: str) -> str:
    # Prepend http schema to url if needed
    p = urlparse(website_link, 'http')
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    # if not netloc.startswith('www.'):
    #     netloc = 'www.' + netloc
    p = ParseResult(p.scheme, netloc, path, *p[3:])
    return p.geturl()
