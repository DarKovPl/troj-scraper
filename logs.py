from datetime import datetime


class WorkLogs:

    def __init__(self):
        self.datetime_now_RR_MM_DD_HHMMSS = str(datetime.now())[:-7].replace('-', '_').replace(' ', '_')
        self.datetime_now_RR_MM_DD = str(datetime.now())[:10].replace('-', '_').replace(' ', '_')
        self.main_pages_log_path = 'logs/work_logs/main_pages_urls/'
        self.request_information_path = 'logs/work_logs/request_information/'
        self.advert_information_path = 'logs/work_logs/advert_details/'

    def write_main_page_urls_with_settings_inf(self, main_pages):
        with open(f'{self.main_pages_log_path}main_pages_urls_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(self.datetime_now_RR_MM_DD_HHMMSS + '\n')
            file.write(f'Start ' + '\n')
            for i in main_pages:
                file.write(f'Key of the dict: {i}' + '\n')
                file.write(str(main_pages[i]['header']) + '\n')
                file.write(str(main_pages[i]['https']) + '\n')
                for urls in main_pages[i]['urls']:
                    file.write(urls + '\n')
                file.write('Stop  ' * 30 + '\n')

    def write_request_details(self, request, dict_key):
        with open(f'{self.request_information_path}request_information_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(f'Key of the dict: {dict_key}' + '\n')
            file.write(self.datetime_now_RR_MM_DD_HHMMSS + '\n')
            file.writelines('Url: ' + str(request.url) + '\n')
            file.writelines('Respond header: ' + str(request.headers) + '\n')
            file.writelines('Request header: ' + str(request.request.headers) + '\n')
            file.write('Stop\t' * 10 + '\n')

    def write_advert_details(self, advert):
        with open(f'{self.advert_information_path}advert_details_{self.datetime_now_RR_MM_DD}.log', 'a+') as file:
            file.write(self.datetime_now_RR_MM_DD_HHMMSS + '\n')
            file.writelines(str(advert) + '\n')
            file.write('* ' * 30 + '\n')
