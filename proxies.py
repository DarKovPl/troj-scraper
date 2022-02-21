from datetime import datetime
from environs import Env
import requests


class ProxyList:
    """
    This class provides proxies servers rotation.
    Proxy servers are replaced when new proxies are available (after a specified date).
    """
    def __init__(self):
        self.req_get = requests.get
        self.env = Env()
        self.env.read_env('.env')
        self.api_key = self.env.str('API_KEY')
        self.proxy_path = './proxy_file/proxies.txt'

    def check_refresh_date(self) -> bool:
        """
        This method is checking if there are new different proxies addresses available
        from proxies servers webpage using REST API.

        :return: boolean True or False
        """
        rep_endpoint = self.env.str('REPLACEMENT_PROXY_INFO')

        current_date = str(datetime.now())[:-16].replace('-', '_').replace(' ', '_')
        refresh_date = self.req_get(rep_endpoint, headers={"Authorization": self.api_key})

        ref_date = refresh_date.json()['automatic_refresh_next_at'][:10].replace('-', '_')

        if int(ref_date) < int(current_date):
            return True

        else:
            return False

    def replace_proxies(self):
        """
        This method is responsible for replacing a proxy using API.
        """
        proxy_list_endpoint = self.env.str('PROXY_LIST')

        proxy_list = self.req_get(proxy_list_endpoint, headers={"Authorization": self.api_key})
        with open(self.proxy_path, 'w+') as f:

            for i, v in enumerate(proxy_list.json()['results'], 1):
                proxies = f"{v['proxy_address']}:{v['ports']['http']}:{v['username']}:{v['password']}"

                if i < 100:
                    f.write(proxies + '\n')
                else:
                    f.write(proxies)
