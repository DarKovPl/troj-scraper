from parsers import DataParser, UrlRequest, RequestParameters
from threading import Event


def main():
    pages_range = []
    urls = []
    main_advertise_urls_with_settings = {}

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

    for page in UrlRequest().get_content(main_advertise_urls_with_settings):
        print(page.url)
        print(page.headers)
        print(page.cookies)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
