from parsers import DataParser, UrlRequest
from threading import Event


def main():
    for page in UrlRequest().get_content():
        request_header = page.request.headers
        response_cookies = page.cookies
        response_headers = page.headers
        response_link = page.url

        print('Start ' * 70)
        # print(page_content)
        print(response_link)
        print('------------------')
        print(request_header)
        print('------------------')
        print(response_cookies)
        print('------------------')
        print(response_headers)
        print()
        print('%' * 400)
        Event().wait(5)

if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
