from parsers import DataParser, UrlRequest, RequestParameters
from threading import Event


def main():
    for page in UrlRequest().get_content():

        page_content = DataParser(page.content).get_start_urls_for_activity()
        RequestParameters().set_url_header_proxy_for_request(page_content)

        request_header = page.request.headers
        response_cookies = page.cookies
        response_headers = page.headers
        response_link = page.url

        print('Start ' * 70)
        print("Page content", page_content)
        print('------------------')
        print("Response link", response_link)
        print('------------------')
        print("Request header", request_header)
        print('------------------')
        print("Response cookie", response_cookies)
        print('------------------')
        print("Response headers", response_headers)
        print()
        print('%' * 400)
        Event().wait(5)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
