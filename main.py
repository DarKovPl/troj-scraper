from parsers import DataParser, UrlRequest, RequestParameters
from threading import Event


def main():
    for page in UrlRequest().get_content():

        if page.url == RequestParameters().get_main_page_url()[0]:
            page_urls = DataParser(page.content).get_start_activity_urls_from_main_page()
            RequestParameters().build_start_urls_list(page_urls)

        elif page.url == RequestParameters().get_main_category_endpoint()[0]:
            last_page_number = DataParser(page.content).get_last_page_number()
            RequestParameters().build_page_range_list(int(last_page_number))



        # request_header = page.request.headers
        # response_cookies = page.cookies
        # response_headers = page.headers
        # response_link = page.url
        #
        # print('Start ' * 70)
        # print("Page content", page_content)
        # print('------------------')
        # print("Response link", response_link)
        # print('------------------')
        # print("Request header", request_header)
        # print('------------------')
        # print("Response cookie", response_cookies)
        # print('------------------')
        # print("Response headers", response_headers)
        # print()
        # print('%' * 400)
        Event().wait(5)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
