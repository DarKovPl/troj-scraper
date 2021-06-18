from parsers import DataParser, Links, UrlRequests
from threading import Event


def main():
    links = Links('.env').get_links_from_env()

    for link in links:
        server_response = UrlRequests(link).get_content()
        page_content = DataParser(server_response).get_html_data()

        print('Start ' * 400)
        print(page_content)
        Event().wait(5)
        print('%' * 1700)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
