from environs import Env
from fake_useragent import UserAgent
import random
import math


class RequestParameters:
    """
    One of the jobs of this class is building a fake multi-users' activity using multiple proxies and headers for
    avoiding a ban from a website while collecting data is doing. The second task is to create a combo of URLs
    to collect data from them. Each piece of portion of the right URLs addresses has its own unique proxy address and
    header set static. Before scraping the right URLs advertises, scraper for each proxy address builds history of
    activity in the main page of the website. The number of URLs links are divided flexible to the number of proxies
    that are available.
    """
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
        """
        This method gets from the environment variable start URL address.
        This address is necessary to get information about the page and build fake users' activity.

        :return: list with a front page URL
        """
        self.env.read_env(self.env_path)
        main_page_url = self.env.list('MAIN_PAGE_URL')

        return main_page_url

    def get_main_category_endpoint(self) -> list:
        """
        This method gets from the environment variable an endpoint URL from which the collecting of proper data starts.

        :return: list with URL endpoint
        """
        self.env.read_env(self.env_path)
        main_category_endpoint = self.env.list('MAIN_CATEGORY_ENDPOINT')

        return main_category_endpoint

    def get_skippable_urls(self) -> list:
        """
        This method creates a list of URLs which are without data to collect, and they are skippable.
        These URLs are part of the users "road" to view advertisements.

        :return: list with URLs which data is not to collect
        """
        skip_urls: list = [
            self.get_main_category_endpoint()[0],
            self.get_main_category_endpoint()[0]
            + self.page_filters[0]
        ]
        return skip_urls

    def get_user_agent_header(self) -> dict:
        """
        This method creates a dictionary with a random header from fake_useragent library.

        :return: dictionary with a header
        """
        random_header: dict = {'User-Agent': self.user_agent.random}

        return random_header

    def get_proxies_from_file(self) -> dict:
        """
        This method reads a proxy list from the file and shuffles this list
        for changing every time proxies' requests order.

        :return: dictionary with a proxies' dict as a value
        """
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

    def set_start_activity_settings_for_request(self) -> dict:
        """
        This method picks one proxy from the proxies and creates a kit with unique settings for sending one request.
        From page is grabbing the last page number and other important data necessary to begin to collect data.

        :return: dictionary with settings for first "scanning" request
        """
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
        """
        This method builds a fake users' activity using a random advertises from random categories of the front page.
        The user has history of session, and he does not show up from nowhere browsing the advertises.

        :param urls_from_main_page: list of the random advertises from random categories
        :return: list of ordered start URLs for every user
        """
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
        """
        This method builds a list of number of all main pages with single advertises.

        :param number_of_pages: number of the last page in the website
        :return: list of all main pages
        """
        self.main_pages_creator.extend(
            self.get_main_category_endpoint()[0]
            + ''.join(part_url for part_url in self.page_filters)
            + str(number) for number in range(number_of_pages + 1)
        )

        return self.main_pages_creator

    def mix_advertises_pages(self, pages_range: list) -> list:
        """
        This method creates a list with mixed main pages URLs. The "mixer" adjusts the number of advertises to a number
        of available proxies and balance the number of requests to every proxy avoiding a situation where one proxy
        has many requests and another proxy has zero.
        For every proxy's, URLs are also a little shuffle between each other.
        This is for masking clicking one by one advertisement in the same sequence.

        :param pages_range: list of main pages
        :return: list with lists of prepared URLs
        """
        self.urls_list.clear()
        divided: float = len(pages_range) / len(self.proxies)
        fra, whole = math.modf(divided)
        fractional: float = 0
        main_pages: list = []

        for _ in range(len(self.proxies) + 1):
            for _ in range(int(whole) + 1):
                if len(pages_range) > 0:
                    if fractional > 1:
                        fractional = 0
                        continue
                    main_pages.append(pages_range.pop(0))

                main_pages_copy = main_pages[1::2]
                random.shuffle(main_pages_copy)
                main_pages[1::2] = main_pages_copy
                fractional += fra

            self.urls_list.append(main_pages.copy())
            main_pages.clear()

        self.urls_list = self.urls_list[:-1] if self.urls_list[-1] == [] else self.urls_list
        random.shuffle(self.urls_list)

        return self.urls_list

    def set_settings_for_main_advertise_list(self, main_list_urls: list) -> dict:
        """
        This method creates a dictionary with all necessary data for a request to a web page.
        Settings from this method are saved for each proxy, and they are using to collect data from advertises.

        :param main_list_urls: list of main pages URLs
        :return: dictionary with a requests settings
        """
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
        """
        This method copy the request settings for the right URLs.

        :param key: key of currently collecting set of URLs
        :param urls: list of the right URLs
        :return: dictionary with a set to collect
        """
        self.single_list_links_settings = self.url_header_proxy[key].copy()
        self.single_list_links_settings['urls'] = urls
        self.single_list_links_settings = {f"{key}": self.single_list_links_settings}

        return self.single_list_links_settings

    def add_all_single_adverts_links(self, dict_key: str, urls_settings: dict) -> dict:
        """
        TO DO

        :param dict_key:
        :param urls_settings:
        :return:
        """
        if dict_key in self.all_single_adverts_links:
            for i in urls_settings.get(dict_key).get('urls'):
                self.all_single_adverts_links[dict_key]['urls'].append(i)

            return self.all_single_adverts_links

        while dict_key not in self.all_single_adverts_links:
            self.all_single_adverts_links.update(urls_settings)

        return self.all_single_adverts_links

    def balance_single_advert_request(self, urls_settings: dict) -> str:
        """
        This method balances usage of dict_key and prevents a situation where one proxy gets many requests one by one.
        This method also remove disproportion with number of the right URLs.

        :param urls_settings: dictionary with request settings
        :return: dict_key number with the highest number of URLs
        """
        if (self.forbidden_key in urls_settings) and (len(urls_settings) > 1):
            urls_settings.pop(self.forbidden_key)

        if len(urls_settings) > 1:

            parameters: list = [([k] * len(v.get('urls'))) for k, v in urls_settings.items() if v.get('urls')]
            dict_keys: list = [str_keys for n in [v for v in parameters if v != 0] for str_keys in n]

            dict_key = random.choice(dict_keys)
            self.forbidden_key = dict_key

            return dict_key

        else:
            dict_key, _ = urls_settings.popitem()
            self.forbidden_key = dict_key

            return dict_key

    @staticmethod
    def get_highest_number_of_links(main_pages: dict) -> str:
        """
        This method balances usage of dict_key and picks a key with the highest number of URLs.

        :param main_pages: dictionary with a main pages URLs settings
        :return: dict_key number with the highest number of URLs
        """
        main_pages: list = [(k, len(v['urls'])) for k, v in main_pages.items()]
        dict_key: str = max(main_pages, key=lambda k: k[1])[0]

        return dict_key

    @staticmethod
    def check_number_main_page_links(main_page_links: dict) -> bool:
        """
        This method checks if there are main page URLs to query.

        :param main_page_links: dictionary with a main page URLs
        :return: True or False
        """
        for k, v in main_page_links.items():
            if len(v['urls']) > 0:
                return True

        return False
