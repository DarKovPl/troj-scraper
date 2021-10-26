import os.path
from datetime import datetime
import os
import math


file_date = str(datetime.now())[:10].replace('-', '_').replace(' ', '_')


class FolderStructure:

    def __init__(self):
        self.main_pages_settings_path = 'logs/work_logs/main_pages_urls/'
        self.main_pages_req_inf_path = 'logs/work_logs/main_pages_req_inf/'
        self.advert_inf_path = 'logs/work_logs/request_advert_inf/'
        self.time_to_end_path = 'logs/work_logs/'
        self.parser_log_path = 'logs/error_logs/parser_error/'
        self.request_log_path = 'logs/error_logs/request_error/'
        self.database_log_path = 'logs/error_logs/database_error/'
        self.databases_path = 'databases/'
        self.sessions_path = 'sessions/'
        self.proxy_path = 'proxy_file/'


class LogsStructureCreator(FolderStructure):

    def __init__(self):
        super().__init__()
        self.folder_structure_instance = FolderStructure()
        self.datetime_now_RR_MM_DD_HHMMSS = str(datetime.now())[:-7].replace('-', '_').replace(' ', '_')

    def create_folder_structure(self):

        for path in vars(self.folder_structure_instance).values():
            if not os.path.exists(path):
                os.makedirs(path)


class WorkLogs(LogsStructureCreator):

    def __init__(self, request=None, dict_key=None, urls_with_settings=None):
        super().__init__()
        self.request = request
        self.dict_key = dict_key
        self.urls_with_settings = urls_with_settings

    def write_main_page_urls_with_settings_inf(self):
        with open(f'{self.main_pages_settings_path}main_pages_urls_{file_date}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Start \n')
            for i in self.urls_with_settings:
                file.write(f'Key of the dict: {i}\n')
                file.write(f"Header: {str(self.urls_with_settings[i]['header'])}\n")
                file.write(f"Proxy: {str(self.urls_with_settings[i]['https'])}\n")
                for urls in self.urls_with_settings[i]['urls']:
                    file.write(urls + '\n')
                file.write('Stop  ' * 50 + '\n')

    def write_main_pages_req_and_resp_inf(self):
        with open(f'{self.main_pages_req_inf_path}main_pages_req_inf_{file_date}.log', 'a+') as file:
            file.write(f'Key of the dict: {self.dict_key}\n')
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.writelines(f'Url: {str(self.request.url)}\n')
            file.writelines(f'Respond header: {str(self.request.headers)}\n')
            file.writelines(f'Request header: {str(self.request.request.headers)}\n')
            file.write('Stop\t' * 10 + '\n')

    def write_advert_req_inf(self):
        with open(f'{self.advert_inf_path}advert_information_{file_date}.log', 'a+') as file:
            advert_url = self.urls_with_settings[self.dict_key]['urls'][0]
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Key of the dict: {self.dict_key}\n')
            file.write(f"Advert url: {advert_url}\n")
            file.write(f"Header: {self.urls_with_settings[self.dict_key]['header']}\n")
            file.write(f"Proxy: {self.urls_with_settings[self.dict_key]['https']}\n")
            file.write('* ' * 50 + '\n')

    def measure_roughly_time_to_finish(self, scrap_time=None, adverts_figure=None):
        import wdb;
        wdb.set_trace()
        if adverts_figure is not None:
            time_divided = (adverts_figure * scrap_time) / 60 / 60
            fra, whole = math.modf(time_divided)
            time_to_end = f'{int(whole)}:{round(fra, 1) / 60}'
            path = f'{self.time_to_end_path}to_end_{time_to_end}.log'

            with open(path, 'a') as file:
                file.write(f'{adverts_figure}')

        else:
            with open(os.listdir(self.time_to_end_path)[0], 'r') as file:
                adverts_figure = int(file.readline())
                adverts_figure -= 1
                time_divided = (adverts_figure * scrap_time) / 60 / 60
                fra, whole = math.modf(time_divided)
                time_to_end = f'{whole}:{60 / round(fra, 1)}'

            os.remove(os.listdir(self.time_to_end_path)[0])
            path = f'{self.time_to_end_path}to_end_{time_to_end}.log'

            with open(path, 'a') as file:
                file.write(f'{adverts_figure}')


class ErrorLogs(LogsStructureCreator):

    def __init__(self, exception_message):
        super().__init__()
        self.exception_message = str(exception_message)

    def parser_error_log(self, advert_url):
        with open(f'{self.parser_log_path}parser_error_{file_date}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Advert url: {advert_url}\n')
            file.write(f'Traceback Message:\n{self.exception_message}\n')
            file.write('* ' * 50 + '\n')

    def database_error_log(self, advert_url):
        with open(f'{self.database_log_path}database_error_{file_date}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Advert url: {advert_url}\n')
            file.write(f'Traceback Message:\n{self.exception_message}\n')
            file.write('* ' * 50 + '\n')

    def request_error_log(self, advert_url):
        with open(f'{self.request_log_path}request_error_{file_date}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Advert url: {advert_url}\n')
            file.write(f'Traceback Message:\n{self.exception_message}\n')
            file.write('* ' * 50 + '\n')
