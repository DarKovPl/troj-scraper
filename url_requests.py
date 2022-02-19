from logs import ErrorLogs
from requests import Session, Request, exceptions
from threading import Event
import pickle
import traceback


class UrlRequest:
    """
    This class is responsible for sending query to a web page through a proxy.
    Class creates a session using requests module and session files using pickle module.
    """

    def __init__(self):
        self.session = Session()
        self.request = Request

    def get_content(self, scrap_set: dict):
        """
        This method gets content from main pages.

        :param scrap_set: dictionary with a URLs settings
        :return: response object with data from a web page
        """
        for key in scrap_set:
            session = self.session
            session.cookies.clear()

            for link in scrap_set[key]['urls']:
                Event().wait(0.01)
                request = self.request('GET', link, headers=scrap_set[key]['header'])
                prepped = session.prepare_request(request)
                Event().wait(0.01)
                try:
                    response = session.send(prepped, proxies=scrap_set[key], timeout=10, stream=True)
                    yield response
                    response.close()

                except exceptions.ConnectionError as e:
                    ErrorLogs(f'{e}\n{traceback.format_exc()}').request_error_log(link)
                    Event().wait(10)
                    scrap_set[key]['urls'].insert(0, scrap_set[key]['urls'][scrap_set[key]['urls'].index(link)])
                    pass

                except exceptions.ReadTimeout as e:
                    ErrorLogs(f'{e}\n{traceback.format_exc()}').request_error_log(link)
                    Event().wait(10)
                    scrap_set[key]['urls'].insert(0, scrap_set[key]['urls'][scrap_set[key]['urls'].index(link)])
                    pass

                except Exception as e:
                    ErrorLogs(f'{e}\n{traceback.format_exc()}').request_error_log(link)
                    continue

    def get_advert_content(self, scrap_set: dict, dict_key: str):
        """
        This method gets content from the right advertise pages.

        :param scrap_set: dictionary with a URLs settings
        :param dict_key: dict_key number
        :return: response object with data from a web page

        TODO: Generator in the except block is necessary?
        """
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
        try:
            response = session.send(prepped, proxies=scrap_set, timeout=10, stream=True)

            with open(f'sessions/session_{dict_key}.pkl', 'wb') as file:
                pickle.dump(session, file)

            yield response
            response.close()

        except exceptions.ConnectionError as e:
            ErrorLogs(f'{e}\n{traceback.format_exc()}').request_error_log(link)
            Event().wait(10)
            scrap_set['urls'].insert(0, link)
            yield None

        except exceptions.ReadTimeout as e:
            ErrorLogs(f'{e}\n{traceback.format_exc()}').request_error_log(link)
            Event().wait(10)
            scrap_set['urls'].insert(0, link)
            yield None

        except Exception as e:
            ErrorLogs(f'{e}\n{traceback.format_exc()}').request_error_log(link)
            yield None
