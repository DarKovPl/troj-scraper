from bs4 import BeautifulSoup
from environs import Env
from requests import Session, Request
from fake_useragent import UserAgent
from threading import Event


class DataParser:
    def __init__(self, data: bytes):
        self.data = data

    def get_html_data(self):
        soup = BeautifulSoup(self.data, "lxml")
        # import wdb; wdb.set_trace()
        return soup.prettify()

    def get_start_url_property(self):
        soup = BeautifulSoup(self.data, "lxml")
        property_advert = soup.find('div', class_='section__ogl section__ogl--nieruchomosci')
        sorted_ = []
        for content in property_advert.findAll('div', class_='front__ogl__content'):
            url = [content.find('a')['href']]
            price = content.find('p', class_='front__ogl__price__value')
            sorted_ += [(url, price) for url, price in zip(url, price)]
        sorted_ = sorted(sorted_, key=lambda i: i[1])
        sorted_.reverse()
        best_offer = sorted_[0][0]
        return best_offer


class RequestParameters(DataParser):

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
        self.set_url_header_proxy_for_request()

    def get_main_categories_urls(self):
        self.env.read_env(self.env_path)
        main_categories_urls_dict = self.env.json('MAIN_CATEGORIES_URL')
        main_categories = (url for url in main_categories_urls_dict.values())
        return main_categories

    def get_user_activity_urls(self):
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

    def mix_urls_for_fake_activity(self, gotten_urls):
        import wdb;
        wdb.set_trace()
        urls_start_list = [url for url in zip(self.get_user_activity_urls(), gotten_urls)]
        return urls_start_list

    def set_url_header_proxy_for_request(self):
        for key in self.get_proxies_from_file():
            self.url_header_proxy.update({f"{key}": {"urls": [url for url in self.mix_urls_for_fake_activity(self.get_start_url_property())],
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
        # import wdb;
        # wdb.set_trace()
        for key in self.url_header_proxy:
            session = self.session
            session.cookies.clear()
            for link in self.url_header_proxy[key]['urls']:
                request = self.request('GET', link, headers=self.url_header_proxy[key]['header'])
                prepped = session.prepare_request(request)
                response = session.send(prepped, proxies=self.url_header_proxy[key])
                yield response
