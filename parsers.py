from bs4 import BeautifulSoup
from environs import Env
from requests import Session, Request
from fake_useragent import UserAgent
from threading import Event
import re
import random


class RequestParameters:

    def __init__(self):
        self.env_path = '.env'
        self.env = Env()
        self.user_agent = UserAgent()
        self.session = Session()
        self.request = Request
        self.proxies_file_path = 'proxy_file/proxies.txt'
        self.proxies = {'0': {'Proxy Address': 0,
                              'Port': 0,
                              'Username': 0,
                              'Password': 0
                              }
                        }
        self.url_header_proxy = {}
        self.set_start_activity_url()

    def get_main_categories_urls(self):
        self.env.read_env(self.env_path)
        main_categories_urls_dict = self.env.json('MAIN_CATEGORIES_URL')
        main_categories = (url for url in main_categories_urls_dict.values())
        return main_categories

    def get_main_user_activity_url(self):
        self.env.read_env(self.env_path)
        user_activity_urls_dict = self.env.json('START_USER_ACTIVITY')
        user_activity = (url for url in user_activity_urls_dict.values())
        return user_activity

    def get_user_agent_header(self):
        random_header = {'User-Agent': self.user_agent.random}
        return random_header

    def get_proxies_from_file(self):
        with open(self.proxies_file_path, 'r') as file:
            for i, line in enumerate(file.readlines()):
                line = line.rstrip('\n')
                proxy_setup = line.split(':')
                self.proxies.update({str(i): {key: value for key, value in zip(self.proxies['0'].keys(), proxy_setup)}})
            return self.proxies

    # def mix_urls_for_fake_activity(self, urls):
    #     # import wdb;
    #     # wdb.set_trace()
    #     urls_start_list = [url for url in urls]
    #     return urls_start_list

    def set_start_activity_url(self):
        for key in self.get_proxies_from_file():
            self.url_header_proxy.update(
                {f"{key}": {"urls": [url for url in self.get_main_user_activity_url()],
                            "header": self.get_user_agent_header(),
                            "http": f"http://{self.proxies[key]['Username']}:"
                                    f"{self.proxies[key]['Password']}@"
                                    f"{self.proxies[key]['Proxy Address']}:"
                                    f"{self.proxies[key]['Port']}"
                            }
                 })
            break

    def set_url_header_proxy_for_request(self, urls):
        import wdb;
        wdb.set_trace()
        zipped = list(map(lambda e: (e, next(iter(self.get_main_user_activity_url()))), urls))
        tuple_unpack = [b for a in zipped for b in a]
        for key in self.get_proxies_from_file():
            self.url_header_proxy.update(
                {f"{key}": {"urls":  tuple_unpack,
                            "header": self.get_user_agent_header(),
                            "http": f"http://{self.proxies[key]['Username']}:"
                                    f"{self.proxies[key]['Password']}@"
                                    f"{self.proxies[key]['Proxy Address']}:"
                                    f"{self.proxies[key]['Port']}"
                            }
                 })


class UrlRequest(RequestParameters):

    # def create_user_fake_activity(self):

    def get_content(self):
        for key in self.url_header_proxy:
            session = self.session
            session.cookies.clear()
            for link in self.url_header_proxy[key]['urls']:
                request = self.request('GET', link, headers=self.url_header_proxy[key]['header'])
                prepped = session.prepare_request(request)
                response = session.send(prepped, proxies=self.url_header_proxy[key])
                yield response


class DataParser:
    def __init__(self, data: bytes):
        self.data = data

    def get_html_data(self):
        soup = BeautifulSoup(self.data, "lxml")
        return soup.prettify()

    def get_start_urls_for_activity(self):
        soup = BeautifulSoup(self.data, "lxml")
        all_advert = soup.find('div', class_='section-content')
        urls = []
        for container in all_advert.findAll('div', class_='section__container'):
            for section in container.findAll('div', class_=re.compile("section__ogl section__ogl")):
                for content in section.findAll('div', class_='front__ogl__content__title'):
                    url = [content.find('a')['href']]
                    urls.extend(url)
        number = random.randrange(3, 6)
        random_urls = random.sample(urls, number)
        return random_urls
