from bs4 import BeautifulSoup
from environs import Env
from requests import Session, Request
from fake_useragent import UserAgent
from threading import Event


class RequestParameters:

    def __init__(self):
        self.env_path = '.env'
        self.env = Env()
        self.user_agent = UserAgent()
        self.session = Session()
        self.request = Request
        self.proxies_file_path = 'proxy_file/proxies.txt'
        self.proxies = {
            '0': {'Proxy Address': 0,
                  'Port': 0,
                  'Username': 0,
                  'Password': 0
                  }
        }
        self.url_header_proxy = {}
        self.set_header_proxy_for_request()

    def get_links_from_env(self):
        self.env.read_env(self.env_path)
        url_dict = self.env.json('URL_ADDRESSES')
        urls = (url for url in url_dict.values())
        return urls

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

    def set_header_proxy_for_request(self):
        import wdb;
        wdb.set_trace()
        for i, link in enumerate(self.get_links_from_env()):
            i = str(i)
            self.url_header_proxy.update({f"{i}": {"url": link,
                                                   "header": self.get_user_agent_header(),
                                                   "http": f"http://{self.get_proxies_from_file()[i]['Username']}:"
                                                           f"{self.get_proxies_from_file()[i]['Password']}@"
                                                           f"{self.get_proxies_from_file()[i]['Proxy Address']}:"
                                                           f"{self.get_proxies_from_file()[i]['Port']}"
                                                   }
                                          })


class UrlRequest(RequestParameters):

    # def get_response_from_main_page(self):
    #     main_page_request = self.request(
    #         self.set_proxy_for_request_url()['0']["url"],
    #         headers=self.set_proxy_for_request_url()['0']["header"],
    #     )
    #     return main_page_request

    def get_content(self):

        for key in self.url_header_proxy:
            # import wdb;
            # wdb.set_trace()
            # first_request = session.request('GET', self.set_proxy_for_request_url()['0']["url"],
            #                                 headers=self.set_proxy_for_request_url()['0']["header"],
            #                                 proxies=self.set_proxy_for_request_url()['0'])
            # first_prepped = session.prepare_request(first_request)
            # resp = session.send(first_prepped, proxies=self.set_proxy_for_request_url()['0'])

            request = self.request('GET', self.url_header_proxy[key]['url'],
                                   headers=self.url_header_proxy['0']['header'])

            prepped = self.session.prepare_request(request)
            response = self.session.send(prepped,
                                         proxies=self.url_header_proxy['0'])
            yield response


class DataParser:
    def __init__(self, data: bytes):
        self.data = data

    def get_html_data(self):
        bs = BeautifulSoup(self.data, "lxml")
        # import wdb; wdb.set_trace()
        return bs.prettify()
