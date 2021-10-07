from datetime import datetime


class WorkLogs:

    def __init__(self):
        self.datetime_now_RR_MM_DD_HHMMSS = str(datetime.now())[:-7].replace('-', '_').replace(' ', '_')
        self.datetime_now_RR_MM_DD = str(datetime.now())[:10].replace('-', '_').replace(' ', '_')
        self.main_pages_settings_path = 'logs/work_logs/main_pages_urls/'
        self.main_pages_req_inf_path = 'logs/work_logs/main_pages_req_inf/'
        self.advert_inf_path = 'logs/work_logs/request_advert_inf/'

    def write_main_page_urls_with_settings_inf(self, main_pages):
        with open(f'{self.main_pages_settings_path}main_pages_urls_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Start \n')
            for i in main_pages:
                file.write(f'Key of the dict: {i}\n')
                file.write(f"Header: {str(main_pages[i]['header'])}\n")
                file.write(f"Proxy: {str(main_pages[i]['https'])}\n")
                for urls in main_pages[i]['urls']:
                    file.write(urls + '\n')
                file.write('Stop  ' * 30 + '\n')

    def write_main_pages_req_and_resp_inf(self, request, dict_key):
        with open(f'{self.main_pages_req_inf_path}main_pages_req_inf_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Key of the dict: {dict_key}\n')
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.writelines(f'Url: {str(request.url)}\n')
            file.writelines(f'Respond header: {str(request.headers)}\n')
            file.writelines(f'Request header: {str(request.request.headers)}\n')
            file.write('Stop\t' * 10 + '\n')

    def write_advert_req_inf(self, advert_urls, dict_key):
        with open(f'{self.advert_inf_path}advert_information_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Key of the dict: {dict_key}\n')
            file.write(f"Advert url: {advert_urls[dict_key]['urls'][0]}\n")
            file.write(f"Header: {advert_urls[dict_key]['header']}\n")
            file.write(f"Proxy: {advert_urls[dict_key]['https']}\n")
            file.write('* ' * 30 + '\n')


class ErrorLogs(WorkLogs):

    def __init__(self, exception_message):
        super().__init__()
        self.connection_error_log_path = 'logs/error_logs/connection_error/'
        self.proxy_error_log_path = 'logs/error_logs/proxy_error/'
        self.exception_message = str(exception_message)

    def proxy_error(self):
        with open(f'{self.proxy_error_log_path}ProxyError_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Time: {self.datetime_now_RR_MM_DD_HHMMSS}\n')
            file.write(f'Message:\n' + self.exception_message)
