from bs4 import BeautifulSoup
from environs import Env
from requests import get

env = Env()
env.read_env('./.env')

page = get(env.json('URL_ADDRESSES')['ACCOMMODATION'])
bs = BeautifulSoup(page.content, 'html.parser')

page = get(env.json('URL_ADDRESSES')['I_WILL_BUY'])
bs_1 = BeautifulSoup(page.content, 'html.parser')

