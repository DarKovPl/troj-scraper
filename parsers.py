from bs4 import BeautifulSoup
from environs import Env
from requests import get
from threading import Event


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


class UrlParser:
    def __init__(self, url):
        self.url = url

    def get_html_data(self):
        page = get(self.url)
        bs = BeautifulSoup(page.content, "html.parser")
        Event().wait(10)
        return bs
