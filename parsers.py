from bs4 import BeautifulSoup
from environs import Env
from requests import get
from threading import Event
from lxml import html

class Links:

    def __init__(self, env_path: str):
        self.env_path = env_path
        self.env = Env()

    def get_links_from_env(self):
        self.env.read_env(self.env_path)
        url_dict = self.env.json('URL_ADDRESSES')
        urls = (url for url in url_dict.values())
        for url in urls:
            yield url


class UrlRequests:

    def __init__(self, url, headers='', cookies=''):
        self.url = url
        self.headers = headers
        self.cookies = cookies

    def get_request(self):
        response = get(self.url)
        return response


class DataParser:
    def __init__(self, bytes_data):
        self.bytes_data = bytes_data

    def get_html_data(self):
        bs = BeautifulSoup(self.bytes_data, 'lxml')
        Event().wait(10)
        return bs.decode(pretty_print=True)

