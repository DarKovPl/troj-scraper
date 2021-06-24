from parsers import DataParser, UrlRequest
from threading import Event


def main():
    for server_response in UrlRequest().get_content():
        page_content = DataParser(server_response[0]).get_html_data()
        request_header = server_response[1]
        response_cookies = server_response[2]

        print('Start ' * 400)
        # print(page_content)
        print(request_header)
        print(response_cookies)
        print('%' * 1700)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
