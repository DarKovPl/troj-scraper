from parsers import DataParser, Links, UrlRequests


def main():
    links = Links.get_links_from_env(Links('./.env'))

    for link in links:
        server_response = UrlRequests(link)
        page_content = DataParser(server_response).get_html_data
        print('Start ' * 400)
        print(page_content)
        print('%' * 1700)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
