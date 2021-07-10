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

    def get_beginning_user_activity_url(self):
        self.env.read_env(self.env_path)
        user_activity_url = self.env.list('START_USER_ACTIVITY')
        return user_activity_url

    def get_main_category_estates_url(self):
        self.env.read_env(self.env_path)
        main_category_url = self.env.list('MAIN_CATEGORY_ESTATES')
        return main_category_url

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

    def set_start_activity_url(self):
        for key in sorted(list(self.get_proxies_from_file())[1:], key=lambda x:  random.random()):
            self.url_header_proxy.update(
                {f"{key}": {"urls": self.get_beginning_user_activity_url(),
                            "header": self.get_user_agent_header(),
                            "http": f"http://{self.proxies[key]['Username']}:"
                                    f"{self.proxies[key]['Password']}@"
                                    f"{self.proxies[key]['Proxy Address']}:"
                                    f"{self.proxies[key]['Port']}"
                            }
                 })
            break

    def set_urls_headers_proxies_for_requests(self, urls):
        import wdb;
        wdb.set_trace()
        to_by_turns = list(map(lambda e: (e, self.get_beginning_user_activity_url()[0]), urls))
        by_turns_list_urls = [url for tup_set in to_by_turns for url in tup_set]
        by_turns_list_urls.reverse()
        for key in self.get_proxies_from_file():
            self.url_header_proxy.update(
                {f"{key}": {"urls":  by_turns_list_urls,
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
