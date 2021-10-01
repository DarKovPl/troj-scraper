from requests import Session, Request
from threading import Event
import pickle


class UrlRequest:
    def __init__(self):
        self.session = Session()
        self.request = Request

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

    def get_advert_content(self, scrap_set, dict_key):
        try:
            with open(f'sessions/session_{dict_key}.pkl', 'rb') as file:
                session = pickle.load(file)
        except IOError:
            session = self.session

        link = scrap_set['urls'].pop(0)
        Event().wait(0.01)
        request = self.request('GET', link, headers=scrap_set['header'])
        prepped = session.prepare_request(request)
        Event().wait(0.01)
        response = session.send(prepped, proxies=scrap_set, timeout=10, stream=True)

        with open(f'sessions/session_{dict_key}.pkl', 'wb') as file:
            pickle.dump(session, file)

        yield response
        response.close()
