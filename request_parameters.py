from environs import Env
from fake_useragent import UserAgent
import random
import math


class RequestParameters:

    def __init__(self):
        self.env_path: str = '.env'
        self.env = Env()
        self.user_agent = UserAgent()
        self.proxies_file_path: str = 'proxy_file/proxies.txt'
        self.page_filters: list = ['o1,1.html', '?strona=']
        self.proxies: dict = {
            '0': {
                'Proxy Address': 0,
                'Port': 0,
                'Username': 0,
                'Password': 0
            }
        }
        self.url_header_proxy: dict = {}
        self.urls_list: list = []
        self.main_pages_creator: list = []
        self.single_list_links_settings: dict = {}
        self.all_single_adverts_links: dict = {}
        self.forbidden_key: str = ''

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
        random_header: dict = {'User-Agent': self.user_agent.random}

        return random_header

    def get_proxies_from_file(self) -> dict:
        proxy_setup: list = []
        with open(self.proxies_file_path, 'r') as file:
            for i, line in enumerate(file.readlines()):
                line = line.rstrip('\n')
                proxy = line.split(':')
                proxy_setup.append(proxy)

        random.shuffle(proxy_setup)

        for i in range(len(proxy_setup)):
            self.proxies.update(
                {str(i): {key: value for key, value in zip(self.proxies['0'].keys(), proxy_setup.pop(0))}}
            )

        return self.proxies

    def set_start_activity_settings_for_requests(self) -> dict:
        for key in sorted(list(self.get_proxies_from_file())[1:], key=lambda x: random.random()):
            self.url_header_proxy.update(
                {
                    f"{key}": {
                        "urls": self.get_main_page_url() + self.get_main_category_endpoint(),
                        "header": self.get_user_agent_header(),
                        "https": f"http://{self.proxies[key]['Username']}:"
                                 f"{self.proxies[key]['Password']}@"
                                 f"{self.proxies[key]['Proxy Address']}:"
                                 f"{self.proxies[key]['Port']}"
                    }
                }
            )
            self.proxies.pop(key)
            break

        start_set: dict = self.url_header_proxy.copy()

        return start_set

    def build_start_urls_list(self, urls_from_main_page: list) -> list:
        self.urls_list.clear()
        to_by_turns = list(map(lambda e: (e, self.get_main_page_url()[0]), urls_from_main_page))
        by_turns_list_urls = [url for tup_set in to_by_turns for url in tup_set]
        by_turns_list_urls.reverse()

        last_urls: list = self.get_main_page_url() + self.get_main_category_endpoint() + [
            self.get_main_category_endpoint()[0]
            + self.page_filters[0]
        ]

        by_turns_list_urls.extend(last_urls)
        self.urls_list.append(by_turns_list_urls)

        return self.urls_list

    def build_page_range_list(self, number_of_pages: int) -> list:
        self.main_pages_creator.extend(
            self.get_main_category_endpoint()[0]
            + ''.join(part_url for part_url in self.page_filters)
            + str(number) for number in range(number_of_pages + 1)  # heererererer
        )

        return self.main_pages_creator

    def mix_advertises_pages(self, pages_range: list) -> list:
        self.urls_list.clear()
        divided: float = len(pages_range) / len(self.proxies)
        fra, whole = math.modf(divided)
        fractional: float = fra
        main_pages: list = []

        for _ in range(len(self.proxies) + 1):
            for _ in range(0, int(whole) + 1):
                if len(pages_range) > 0:
                    main_pages.append(pages_range.pop(0))

                main_pages_copy = main_pages[1::2]
                random.shuffle(main_pages_copy)
                main_pages[1::2] = main_pages_copy

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
                        "https": f"http://{self.proxies[key]['Username']}:"
                                 f"{self.proxies[key]['Password']}@"
                                 f"{self.proxies[key]['Proxy Address']}:"
                                 f"{self.proxies[key]['Port']}"
                    }
                }
            )
        return self.url_header_proxy

    def copy_settings_from_main_adverts_list(self, key: str, urls: list) -> dict:
        self.single_list_links_settings = self.url_header_proxy[key].copy()
        self.single_list_links_settings['urls'] = urls
        self.single_list_links_settings = {f"{key}": self.single_list_links_settings}

        return self.single_list_links_settings

    def add_all_single_adverts_links(self, dict_key: str, urls_settings: dict) -> dict:
        if dict_key in self.all_single_adverts_links:
            for i in urls_settings.get(dict_key).get('urls'):
                self.all_single_adverts_links[dict_key]['urls'].append(i)

            return self.all_single_adverts_links

        while dict_key not in self.all_single_adverts_links:
            self.all_single_adverts_links.update(urls_settings)

        return self.all_single_adverts_links

    def balance_single_advert_request(self, urls_settings: dict) -> str:
        if (self.forbidden_key in urls_settings) and (len(urls_settings) > 1):
            urls_settings.pop(self.forbidden_key)

        if len(urls_settings) > 1:

            parameters: list = [(k, len(v.get('urls'))) for k, v in urls_settings.items() if v.get('urls')]
            dict_keys: list = [str_keys for n in [str(k) * v for k, v in parameters if v != 0] for str_keys in n]

            dict_key = random.choice(dict_keys)
            self.forbidden_key = dict_key

            return dict_key

        else:
            dict_key, _ = urls_settings.popitem()
            self.forbidden_key = dict_key

            return dict_key

    @staticmethod
    def get_highest_number_of_links(main_pages: dict) -> str:
        main_pages: list = [(k, len(v['urls'])) for k, v in main_pages.items()]
        dict_key: str = max(main_pages, key=lambda k: k[1])[0]

        return dict_key

    @staticmethod
    def check_number_main_page_links(main_page_links: dict) -> bool:
        for k, v in main_page_links.items():
            if len(v['urls']) > 0:
                return True

        return False

    # def check_which_proxies_are_unused(self, main_advertise_urls):
