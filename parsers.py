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
        self.urls_list = []
        self.set_start_activity_parameters()

    def get_main_page_url(self):
        self.env.read_env(self.env_path)
        main_page_url = self.env.list('MAIN_PAGE_URL')
        return main_page_url

    def get_main_category_endpoint(self):
        self.env.read_env(self.env_path)
        main_category_endpoint = self.env.list('MAIN_CATEGORY_ENDPOINT')
        return main_category_endpoint

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

    def set_start_activity_parameters(self):
        for key in sorted(list(self.get_proxies_from_file())[1:], key=lambda x:  random.random()):
            self.url_header_proxy.update(
                {f"{key}": {"urls": self.get_main_page_url() + self.get_main_category_endpoint(),
                            "header": self.get_user_agent_header(),
                            "http": f"http://{self.proxies[key]['Username']}:"
                                    f"{self.proxies[key]['Password']}@"
                                    f"{self.proxies[key]['Proxy Address']}:"
                                    f"{self.proxies[key]['Port']}"
                            }
                 })
            self.proxies.pop(key)
            break

    def build_urls_list(self, urls, number):
        to_by_turns = list(map(lambda e: (e, self.get_main_page_url()[0]), urls))
        by_turns_list_urls = [url for tup_set in to_by_turns for url in tup_set]
        by_turns_list_urls.reverse()
        last_urls = self.get_main_page_url() + self.get_main_category_endpoint() + [self.get_main_category_endpoint()[0] + 'o1,1.html']
        by_turns_list_urls.extend(last_urls)
        self.urls_list.extend(by_turns_list_urls)

    def set_urls_headers_proxies_for_requests(self):
        import wdb;
        wdb.set_trace()

        for key in self.proxies:
            self.url_header_proxy.update(
                {f"{key}": {"urls":  self.urls_list,
                            "header": self.get_user_agent_header(),
                            "http": f"http://{self.proxies[key]['Username']}:"
                                    f"{self.proxies[key]['Password']}@"
                                    f"{self.proxies[key]['Proxy Address']}:"
                                    f"{self.proxies[key]['Port']}"
                            }
                 })
        return self.url_header_proxy


class UrlRequest(RequestParameters):

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
        self.soup = BeautifulSoup(data, "lxml")

    def get_start_activity_urls_from_main_page(self):
        all_advert = self.soup.find('div', class_='section-content')
        urls = []
        for container in all_advert.findAll('div', class_='section__container'):
            for section in container.findAll('div', class_=re.compile("section__ogl section__ogl")):
                for content in section.findAll('div', class_='front__ogl__content__title'):
                    url = [content.find('a')['href']]
                    urls.extend(url)
        number = random.randrange(2, 4)
        random_urls = random.sample(urls, number)
        return random_urls

    def get_last_page_number(self):
        last_page_number = self.soup.find('a', class_='pages__controls__last')['data-page-number']
        return last_page_number
