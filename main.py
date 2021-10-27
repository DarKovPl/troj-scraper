from request_parameters import RequestParameters
from url_requests import UrlRequest
from logs import WorkLogs, ErrorLogs, LogsStructureCreator
from parsers import DataParser
import orm
import traceback
from threading import Event
from datetime import datetime
from collections import OrderedDict

main_pages_urls_and_settings = dict()
request_parameters = RequestParameters()


def get_necessary_information():
    urls = list()
    pages_range = list()

    for page in UrlRequest().get_content(request_parameters.set_start_activity_settings_for_requests()):
        if page.url == request_parameters.get_main_page_url()[0]:
            for _ in range(len(request_parameters.proxies)):
                try:
                    page_urls = DataParser(page.content).get_start_activity_urls_from_main_page()
                    urls.extend(request_parameters.build_start_urls_list(page_urls))

                except AttributeError as e:
                    ErrorLogs(f'{e}\n{traceback.format_exc()}').parser_error_log(page.url)
                    continue

                except Exception as e:
                    ErrorLogs(f'{e}\n{traceback.format_exc()}').parser_error_log(page.url)
                    continue

        elif page.url == request_parameters.get_main_category_endpoint()[0]:
            last_page_number = 72  # DataParser(page.content).get_last_page_number()
            WorkLogs().measure_roughly_time_to_finish(2, int(last_page_number) * 30)
            pages_range.extend(request_parameters.build_page_range_list(int(last_page_number)))
            mixed_advertises: list = request_parameters.mix_advertises_pages(pages_range)

            for i in range(len(request_parameters.proxies)):
                urls[i].extend(mixed_advertises[i])

            main_pages_urls_and_settings.update(request_parameters.set_settings_for_main_advertise_list(urls))

            WorkLogs(urls_with_settings=main_pages_urls_and_settings).write_main_page_urls_with_settings_inf()


def scrape_single_adverts():
    order_dict_key: str = ''
    single_adverts_links = list()

    while len(main_pages_urls_and_settings) > 0:

        main_pages_urls_and_settings_copy: dict = main_pages_urls_and_settings.copy()
        for k, v in main_pages_urls_and_settings_copy.items():
            if len(v['urls']) == 0:
                del main_pages_urls_and_settings[k]

        ordered_dict = OrderedDict(main_pages_urls_and_settings)
        if order_dict_key != '':
            ordered_dict.move_to_end(order_dict_key, last=False)

        for dict_key in ordered_dict if order_dict_key != '' else main_pages_urls_and_settings:
            order_dict_key = ''

            main_page_request = UrlRequest().get_advert_content(
                main_pages_urls_and_settings[dict_key],
                dict_key
            )

            main_page_request = next(main_page_request)
            if main_page_request is None:
                continue

            WorkLogs(request=main_page_request, dict_key=dict_key).write_main_pages_req_and_resp_inf()

            try:
                single_adverts_links.extend(
                    DataParser(main_page_request.content).get_all_advertisements_links_from_main_pages(
                        request_parameters.get_skippable_urls(),
                        main_page_request.url
                    )
                )
            except AttributeError as e:
                ErrorLogs(f'{e}\n{traceback.format_exc()}').parser_error_log(main_page_request.url)
                continue

            except Exception as e:
                ErrorLogs(f'{e}\n{traceback.format_exc()}').parser_error_log(main_page_request.url)
                continue

            if len(single_adverts_links) != 0:

                adverts_urls_with_settings: dict = request_parameters.copy_settings_from_main_adverts_list(
                    dict_key,
                    single_adverts_links.copy()
                )

                advert_urls_to_scrap: dict = request_parameters.add_all_single_adverts_links(
                    dict_key,
                    adverts_urls_with_settings.copy()
                )

                single_adverts_links.clear()

                if len(advert_urls_to_scrap) >= len(main_pages_urls_and_settings):
                    counter: int = 0
                    while len(advert_urls_to_scrap) != 0:

                        WorkLogs(urls_with_settings=advert_urls_to_scrap, dict_key=dict_key).write_advert_req_inf()

                        advert_page = UrlRequest().get_advert_content(advert_urls_to_scrap[dict_key], dict_key)
                        advert_page = next(advert_page)
                        if advert_page is None:
                            counter += 1
                            if counter == 4:
                                advert_urls_to_scrap[dict_key]['urls'].pop(0)
                                counter = 0
                            continue

                        Event().wait(3)
                        try:
                            content = DataParser(advert_page.content)
                            content.get_category_of_advertisement()
                            content.get_advert_title()
                            content.get_advert_link(advert_page.url)
                            content.get_advert_stats()
                            content.get_advert_description()

                            advert_details: dict = content.get_core_details()
                            advert_details.update(content.get_advert_stats())
                            advert_details['Date'] = datetime.now().isoformat(' ', 'seconds')
                            add_advert = orm.ScrapperBase(**advert_details)
                            orm.session.add(add_advert)
                            orm.session.commit()
                            WorkLogs().measure_roughly_time_to_finish(advert_details['Date'])
                            print(advert_details)
                            print('*' * 80)

                        except AttributeError as e:
                            ErrorLogs(f'{e}\n{traceback.format_exc()}').parser_error_log(advert_page.url)
                            pass
                        except TypeError as e:  #base erros
                            ErrorLogs(f'{e}\n{traceback.format_exc()}').database_error_log(advert_page.url)
                            pass
                        except Exception as e:
                            ErrorLogs(f'{e}\n{traceback.format_exc()}').parser_error_log(advert_page.url)
                            pass

                        if len(advert_urls_to_scrap[dict_key]['urls']) == 0:
                            # import wdb;
                            # wdb.set_trace()
                            del advert_urls_to_scrap[dict_key]

                        condition: bool = request_parameters.check_number_main_page_links(
                            main_pages_urls_and_settings
                        )

                        if len(advert_urls_to_scrap) <= 1 and condition is True:
                            order_dict_key = request_parameters.get_highest_number_of_links(
                                main_pages_urls_and_settings.copy()
                            )
                            break

                        elif len(advert_urls_to_scrap) <= 1 and condition is False:
                            Event().wait(10)

                        if len(advert_urls_to_scrap) > 0:
                            dict_key: str = request_parameters.balance_single_advert_request(
                                advert_urls_to_scrap.copy()
                            )


if __name__ == '__main__':
    LogsStructureCreator().create_folder_structure()
    get_necessary_information()
    scrape_single_adverts()
