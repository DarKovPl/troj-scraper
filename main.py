from parsers import UrlParser, Links


def main():
    links = Links.get_links_from_env(Links('./.env'))
    import wdb;

    wdb.set_trace()
    for link in links:
        page_content = UrlParser(link).get_html_data()
        print('Start ' * 400)
        print(page_content)
        print('%' * 1700)


if __name__ == '__main__':
    main()

# import wdb; wdb.set_trace()
