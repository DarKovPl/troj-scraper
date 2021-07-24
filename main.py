from parsers import DataParser, UrlRequest, RequestParameters
from threading import Event


def main():
    pages_range = []
    urls = []
    main_advertise_urls_with_settings = {}
    single_advert_links = []

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
                for i in main_advertise_urls_with_settings:
                    for urls in main_advertise_urls_with_settings[i]['urls']:
                        file_1.write(urls + '\n')
                    file_1.write('Stop\n' * 5)

    for page_1 in UrlRequest().get_content(main_advertise_urls_with_settings):
        Event().wait(8)
        # with open('main_pages_information', 'a+') as file:
        #     file.write('Start\n')
        #     file.writelines(str(page_1.url) + '\n')
        #     file.writelines(str(page_1.headers) + '\n')
        #     file.writelines(str(page_1.request.headers) + '\n')
        #     file.write('Stop\t' * 5 + '\n')
        single_advert_links.extend(
                                   DataParser(page_1.content).get_all_advertisements_links_from_main_pages(
                                                                                request_parameters.get_skippable_urls(),
                                                                                page_1.url
                                                                                                           )
        )

        import wdb;
        wdb.set_trace()
        if len(single_advert_links) != 0:
            second_set_urls = request_parameters.copy_settings_from_main_advert_list(single_advert_links)

            for link in UrlRequest().get_content(second_set_urls):
                Event().wait(8)
                print(link.url)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
