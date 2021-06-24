from bs4 import BeautifulSoup
from environs import Env
from requests import Session
from fake_useragent import UserAgent
from threading import Event


class RequestParameters:

    def __init__(self):
        self.env_path = '.env'
        self.env = Env()
        self.user_agent = UserAgent()
        self.session = Session()

    def get_links_from_env(self):
        self.env.read_env(self.env_path)
        url_dict = self.env.json('URL_ADDRESSES')
        urls = (url for url in url_dict.values())
        return urls

    def get_user_agent_header(self):
        headers = {'User-Agent': str(self.user_agent.random)}
        return headers

    def get_session_cookies(self):
        cookies_ = self.session.cookies
        return cookies_


class UrlRequest(RequestParameters):

    def get_content(self):
        for link in self.get_links_from_env():
            response = self.session.get(link, headers=self.get_user_agent_header(), cookies=self.get_session_cookies())
            yield response.content, response.request.headers, response.cookies
            Event().wait(5)


class DataParser:
    def __init__(self, data: bytes):
        self.data = data

    def get_html_data(self):
        bs = BeautifulSoup(self.data, "lxml")
        # import wdb; wdb.set_trace()
        return bs.prettify()
