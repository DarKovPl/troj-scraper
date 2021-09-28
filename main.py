import orm
from parsers import DataParser, UrlRequest, RequestParameters
from threading import Event
from datetime import datetime
from collections import OrderedDict

pages_range = list()
main_pages_urls_and_settings = dict()
single_adverts_links = list()

request_parameters = RequestParameters()


def get_necessary_information():
    urls = list()

    for page in UrlRequest().get_content(request_parameters.set_start_activity_settings_for_requests()):

        if page.url == request_parameters.get_main_page_url()[0]:
            for _ in range(len(request_parameters.proxies)):
                page_urls = DataParser(page.content).get_start_activity_urls_from_main_page()
                urls.extend(request_parameters.build_start_urls_list(page_urls))

        elif page.url == request_parameters.get_main_category_endpoint()[0]:
            last_page_number = 4  # DataParser(page.content).get_last_page_number()
            pages_range.extend(request_parameters.build_page_range_list(int(last_page_number)))
            mixed_advertises: list = request_parameters.mix_advertises_pages(pages_range)

            for i in range(len(request_parameters.proxies)):
                urls[i].extend(mixed_advertises[i])

            main_pages_urls_and_settings.update(request_parameters.set_settings_for_main_advertise_list(urls))

            with open('links', 'a+') as file_1:
                file_1.write('Start\n')
                file_1.write(str(datetime.now())[:-7].replace('-', '_').replace(' ', '_'))
                for i in main_pages_urls_and_settings:
                    for urls in main_pages_urls_and_settings[i]['urls']:
                        file_1.write(urls + '\n')
                    file_1.write('Stop\n' * 5)


def scrape_single_adverts():
    order_dict_key: str = ''

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

            main_page_request = UrlRequest().get_content_2(
                main_pages_urls_and_settings[dict_key],
                dict_key
            )

            main_page_request = next(main_page_request)
            Event().wait(3)

            with open('main_pages_information', 'a+') as file:
                file.write('Start\n')
                file.writelines(str(main_page_request.url) + '\n')
                file.writelines(str(main_page_request.headers) + '\n')
                file.writelines(str(main_page_request.request.headers) + '\n')
                file.write('Stop\t' * 5 + '\n')

            single_adverts_links.extend(
                DataParser(main_page_request.content).get_all_advertisements_links_from_main_pages(
                    request_parameters.get_skippable_urls(),
                    main_page_request.url
                )
            )

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
                    while len(advert_urls_to_scrap) != 0:

                        advert_page = UrlRequest().get_content_2(advert_urls_to_scrap[dict_key], dict_key)
                        advert_page = next(advert_page)
                        Event().wait(3)

                        content = DataParser(advert_page.content)
                        content.get_category_of_advertisement()
                        content.get_advert_title()
                        content.get_advert_link(advert_page.url)
                        content.get_advert_stats()
                        content.get_advert_description()

                        advert_details: dict = content.get_core_details()
                        advert_details.update(content.get_advert_stats())
                        advert_details['Date'] = datetime.now().isoformat(' ', 'seconds')

                        add_advert = orm.TrojScrapperBase(**advert_details)
                        orm.session.add(add_advert)
                        orm.session.commit()
                        print(advert_details)
                        print('*' * 80)

                        with open('core_deatails', 'a+') as file:
                            file.write(str(datetime.now())[:-7].replace('-', '_').replace(' ', '_') + '\n')
                            file.writelines(str(advert_details) + '\n')
                            file.write('*' * 30 + '\n')

                        if len(advert_urls_to_scrap[dict_key]['urls']) == 0:
                            import wdb;
                            wdb.set_trace()
                            del advert_urls_to_scrap[dict_key]

                        condition: bool = request_parameters.check_number_main_page_links(
                            main_pages_urls_and_settings
                        )

                        if len(advert_urls_to_scrap) <= 1 and condition is True:
                            import wdb;
                            wdb.set_trace()
                            order_dict_key = request_parameters.get_highest_number_of_links(
                                main_pages_urls_and_settings.copy()
                            )
                            break

                        elif len(advert_urls_to_scrap) <= 1 and condition is False:
                            Event().wait(10)

                        if len(advert_urls_to_scrap) > 0:
                            dict_key: str = request_parameters.balance_single_advert_request(
                                advert_urls_to_scrap.copy())


if __name__ == '__main__':
    get_necessary_information()
    scrape_single_adverts()
# import wdb; wdb.set_trace()
