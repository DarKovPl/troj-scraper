import orm
from parsers import DataParser, UrlRequest, RequestParameters
from threading import Event
from datetime import datetime


def main():
    pages_range = []
    urls = []
    main_advertise_urls_with_settings = {}
    single_adverts_links = []

    request_parameters = RequestParameters()

    for page in UrlRequest().get_content(request_parameters.set_start_activity_settings_for_requests()):

        if page.url == request_parameters.get_main_page_url()[0]:
            for _ in range(len(request_parameters.proxies)):
                page_urls = DataParser(page.content).get_start_activity_urls_from_main_page()
                urls.extend(request_parameters.build_start_urls_list(page_urls))

        elif page.url == request_parameters.get_main_category_endpoint()[0]:
            last_page_number = DataParser(page.content).get_last_page_number()
            pages_range.extend(request_parameters.build_page_range_list(int(last_page_number)))
            mixed_advertises: list = request_parameters.mix_advertises_pages(pages_range)

            for i in range(len(request_parameters.proxies)):
                urls[i].extend(mixed_advertises[i])

            main_advertise_urls_with_settings.update(request_parameters.set_settings_for_main_advertise_list(urls))

            with open('links', 'a+') as file_1:
                file_1.write('Start\n')
                file_1.write(str(datetime.now())[:-7].replace('-', '_').replace(' ', '_'))
                for i in main_advertise_urls_with_settings:
                    for urls in main_advertise_urls_with_settings[i]['urls']:
                        file_1.write(urls + '\n')
                    file_1.write('Stop\n' * 5)

    for dict_key in main_advertise_urls_with_settings:
        for page_1 in UrlRequest().get_content(main_advertise_urls_with_settings):
            Event().wait(15)
            # with open('main_pages_information', 'a+') as file:
            #     file.write('Start\n')
            #     file.writelines(str(page_1.url) + '\n')
            #     file.writelines(str(page_1.headers) + '\n')
            #     file.writelines(str(page_1.request.headers) + '\n')
            #     file.write('Stop\t' * 5 + '\n')

            single_adverts_links.extend(
                DataParser(page_1.content).get_all_advertisements_links_from_main_pages(
                    request_parameters.get_skippable_urls(),
                    page_1.url
                )
            )

            if len(single_adverts_links) != 0:
                second_set_urls = request_parameters.copy_settings_from_main_adverts_list(
                    dict_key,
                    single_adverts_links
                )

                for page_2 in UrlRequest().get_content(second_set_urls):
                    Event().wait(12)

                    content = DataParser(page_2.content)

                    content.get_category_of_advertisement()
                    content.get_advert_title()
                    content.get_advert_link(page_2.url)
                    content.get_advert_stats()
                    content.get_advert_description()

                    advert_details: dict = content.get_core_details()
                    advert_details.update(content.get_advert_stats())
                    advert_details['Date'] = datetime.now().isoformat(' ', 'seconds')
                    print(advert_details)

                    add_advert = orm.TrojScrapperBase(**advert_details)
                    orm.session.add(add_advert)
                    orm.session.commit()

                    print(advert_details)
                    # print(advert_stats)
                    print('*' * 80)


                    with open('core_deatails', 'a+') as file:
                        file.write(str(datetime.now())[:-7].replace('-', '_').replace(' ', '_') + '\n')
                        file.writelines(str(advert_details) + '\n')
                        file.write('*' * 30 + '\n')

                single_adverts_links.clear()


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
