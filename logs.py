from datetime import datetime


class WorkLogs:

    def __init__(self, request=None, dict_key=None, dict_with_settings=None):
        self.datetime_now_RR_MM_DD_HHMMSS = str(datetime.now())[:-7].replace('-', '_').replace(' ', '_')
        self.datetime_now_RR_MM_DD = str(datetime.now())[:10].replace('-', '_').replace(' ', '_')
        self.main_pages_settings_path = 'logs/work_logs/main_pages_urls/'
        self.main_pages_req_inf_path = 'logs/work_logs/main_pages_req_inf/'
        self.advert_inf_path = 'logs/work_logs/request_advert_inf/'
        self.request = request
        self.dict_key = dict_key
        self.dict_with_settings = dict_with_settings

    def write_main_page_urls_with_settings_inf(self):
        with open(f'{self.main_pages_settings_path}main_pages_urls_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Start \n')
            for i in self.dict_with_settings:
                file.write(f'Key of the dict: {i}\n')
                file.write(f"Header: {str(self.dict_with_settings[i]['header'])}\n")
                file.write(f"Proxy: {str(self.dict_with_settings[i]['https'])}\n")
                for urls in self.dict_with_settings[i]['urls']:
                    file.write(urls + '\n')
                file.write('Stop  ' * 30 + '\n')

    def write_main_pages_req_and_resp_inf(self):
        with open(f'{self.main_pages_req_inf_path}main_pages_req_inf_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Key of the dict: {self.dict_key}\n')
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.writelines(f'Url: {str(self.request.url)}\n')
            file.writelines(f'Respond header: {str(self.request.headers)}\n')
            file.writelines(f'Request header: {str(self.request.request.headers)}\n')
            file.write('Stop\t' * 10 + '\n')

    def write_advert_req_inf(self):
        with open(f'{self.advert_inf_path}advert_information_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            advert_url = self.dict_with_settings[self.dict_key]['urls'][0]
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Key of the dict: {self.dict_key}\n')
            file.write(f"Advert url: {advert_url}\n")
            file.write(f"Header: {self.dict_with_settings[self.dict_key]['header']}\n")
            file.write(f"Proxy: {self.dict_with_settings[self.dict_key]['https']}\n")
            file.write('* ' * 30 + '\n')
        return advert_url


class ErrorLogs(WorkLogs):

    def __init__(self, exception_message):
        super().__init__()
        self.parser_log_path = 'logs/error_logs/parser_error'
        self.request_log_path = 'logs/error_logs/request_error/'
        self.database_log_path = 'logs/error_logs/database_error/'
        self.exception_message = str(exception_message)

    def parser_error_log(self, advert_url):
        with open(f'{self.parser_log_path}parser_error_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Advert url: {advert_url}\n')
            file.write(f'Message:\n{self.exception_message}\n')

    def database_error_log(self, advert_url):
        with open(f'{self.database_log_path}database_error_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Advert url: {advert_url}\n')
            file.write(f'Message:\n{self.exception_message}\n')
