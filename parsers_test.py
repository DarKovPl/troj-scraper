from parsers import Links, UrlParser


def test_Links_initialization():
    links = Links('./.env')
    assert links


def test_UrlParser():
    url_parser = UrlParser('http://httpbin.org/ststus/200')
    assert url_parser
