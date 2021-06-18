from requests import Request, Session, cookies
from fake_useragent import UserAgent
import pickle

current_session = Session()
user_agent = UserAgent()
headers = {'User-Agent': str(user_agent.random)}

prepped = Request('GET', 'https://ogloszenia.trojmiasto.pl/nieruchomosci/ikl,101_106,o1,1.html', headers=headers).prepare()

reso = current_session.send(prepped)
print(reso.url)
print('-' * 30)
print(reso.cookies)
print('-' * 30)
print(reso.headers)
print('-' * 30)
print(reso.request.headers)
print(reso.request.body)

