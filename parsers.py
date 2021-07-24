from bs4 import BeautifulSoup
from environs import Env
from requests import Session, Request
from fake_useragent import UserAgent
from threading import Event
from unidecode import unidecode
import math
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
        self.page_filters = ['o1,1.html', '?strona=']
        self.proxies = {
            '0': {
                'Proxy Address': 0,
                'Port': 0,
                'Username': 0,
                'Password': 0
            }
        }
        self.url_header_proxy = {}
        self.urls_list = []
        self.main_pages_creator = []

    def get_main_page_url(self) -> list:
        self.env.read_env(self.env_path)
        main_page_url = self.env.list('MAIN_PAGE_URL')
        return main_page_url

    def get_main_category_endpoint(self) -> list:
        self.env.read_env(self.env_path)
        main_category_endpoint = self.env.list('MAIN_CATEGORY_ENDPOINT')
        return main_category_endpoint

    def get_skippable_urls(self) -> list:
        skip_urls: list = [
            self.get_main_category_endpoint()[0],
            self.get_main_category_endpoint()[0]
            + self.page_filters[0]
        ]
        return skip_urls

    def get_user_agent_header(self) -> dict:
        random_header = {'User-Agent': self.user_agent.random}
        return random_header

    def get_proxies_from_file(self) -> dict:
        with open(self.proxies_file_path, 'r') as file:
            for i, line in enumerate(file.readlines()):
                line = line.rstrip('\n')
                proxy_setup = line.split(':')
                self.proxies.update({str(i): {key: value for key, value in zip(self.proxies['0'].keys(), proxy_setup)}})
            return self.proxies

    def set_start_activity_settings_for_requests(self):
        for key in sorted(list(self.get_proxies_from_file())[1:], key=lambda x: random.random()):
            self.url_header_proxy.update(
                {
                    f"{key}": {
                                "urls": self.get_main_page_url() + self.get_main_category_endpoint(),
                                "header": self.get_user_agent_header(),
                                "http": f"http://{self.proxies[key]['Username']}:"
                                        f"{self.proxies[key]['Password']}@"
                                        f"{self.proxies[key]['Proxy Address']}:"
                                        f"{self.proxies[key]['Port']}"
                              }
                 }
            )
            self.proxies.pop(key)
            break

        start_set = self.url_header_proxy.copy()
        return start_set

    def build_start_urls_list(self, urls_from_main_page: list):
        self.urls_list.clear()
        to_by_turns = list(map(lambda e: (e, self.get_main_page_url()[0]), urls_from_main_page))
        by_turns_list_urls = [url for tup_set in to_by_turns for url in tup_set]
        by_turns_list_urls.reverse()

        last_urls = self.get_main_page_url() + self.get_main_category_endpoint() + [
            self.get_main_category_endpoint()[0]
            + self.page_filters[0]
        ]

        by_turns_list_urls.extend(last_urls)
        self.urls_list.append(by_turns_list_urls)
        return self.urls_list

    def build_page_range_list(self, number_of_pages: int):
        self.main_pages_creator.extend(
            self.get_main_category_endpoint()[0]
            + ''.join(part_url for part_url in self.page_filters)
            + str(number) for number in range(number_of_pages + 1)
        )
        return self.main_pages_creator

    def mix_advertises_pages(self, pages_range: list):
        self.urls_list.clear()
        divided: float = len(pages_range) / len(self.proxies)
        fra, whole = math.modf(divided)
        fractional = fra
        main_pages: list = []

        for _ in range(len(self.proxies) + 1):
            for _ in range(0, int(whole) + 1):
                if len(pages_range) > 0:
                    main_pages.append(pages_range.pop(0))

                main_pages_copy = main_pages[1::3]
                random.shuffle(main_pages_copy)
                main_pages[1::3] = main_pages_copy

            if fractional > 1:
                if len(pages_range) > 0:
                    main_pages.append(pages_range.pop(0))
                    fractional = fra

            fractional += fra
            self.urls_list.append(main_pages.copy())
            main_pages.clear()

        self.urls_list = self.urls_list[:-1] if self.urls_list[-1] == [] else self.urls_list
        random.shuffle(self.urls_list)
        return self.urls_list

    def set_settings_for_main_advertise_list(self, main_list_urls: list) -> dict:
        self.url_header_proxy.clear()
        for key in self.proxies:
            self.url_header_proxy.update(
                {
                    f"{key}": {
                                "urls": main_list_urls.pop(0),
                                "header": self.get_user_agent_header(),
                                "http": f"http://{self.proxies[key]['Username']}:"
                                        f"{self.proxies[key]['Password']}@"
                                        f"{self.proxies[key]['Proxy Address']}:"
                                        f"{self.proxies[key]['Port']}"
                                }
                }
            )
        return self.url_header_proxy

    def copy_settings_from_main_advert_list(self, urls: list) -> dict:
        single_advert_links_settings = self.url_header_proxy.copy()
        for key in self.proxies:
            single_advert_links_settings.update(
                {
                    f"{key}": {
                        "urls": urls,

                    }
                }

            )
        return single_advert_links_settings


class UrlRequest(RequestParameters):
    def get_content(self, scrap_set):
        for key in scrap_set:
            session = self.session
            session.cookies.clear()

            for link in scrap_set[key]['urls']:
                Event().wait(0.01)
                request = self.request('GET', link, headers=scrap_set[key]['header'])
                prepped = session.prepare_request(request)
                Event().wait(0.01)
                response = session.send(prepped, proxies=scrap_set[key], timeout=10, stream=True)
                yield response
                response.close()


class DataParser:
    def __init__(self, data: bytes):
        self.soup = BeautifulSoup(data, "lxml")

    def get_start_activity_urls_from_main_page(self) -> list:
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

    def get_last_page_number(self) -> str:
        last_page_number = self.soup.find('a', class_='pages__controls__last')['data-page-number']
        return last_page_number

    def get_all_advertisements_links_from_main_pages(self, forbidden_urls: list, url: str) -> list:
        urls: list = []
        while url not in forbidden_urls:
            for url in self.soup.findAll('a', class_='list__item__content__title__name link'):
                urls.append(url['href'])
            return urls
        return urls

    def get_category_of_advertisement(self) -> str:
        advertise_category = 'None'
        for z in self.soup.findAll('span', itemprop='name')[-1]:
            advertise_category: str = unidecode(z)
        return advertise_category
