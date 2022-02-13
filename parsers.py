from bs4 import BeautifulSoup
from unidecode import unidecode
import re
import random


class DataParser:
    """
    This class is a parser and when we replace this module with another parser module we can
    collect data from other website.
    """
    def __init__(self, data: bytes):
        self.soup = BeautifulSoup(data, "lxml")
        self.advert_details: dict = {'Adres': None}
        self.advert_stats = dict()

    def get_start_activity_urls_from_main_page(self) -> list:
        """
        This method gets all advertise URLs from front page of the website and returns a random number of its.

        :return: list of several advertisements, for building a fake activity
        """
        all_advert = self.soup.find('div', class_='section-content')
        urls = list()

        for container in all_advert.findAll('div', class_='section__container'):
            for section in container.findAll('div', class_=re.compile("section__ogl section__ogl")):
                for content in section.findAll('div', class_='front__ogl__content__title'):
                    url = [content.find('a')['href']]
                    urls.extend(url)

        number = random.randrange(0, 4)
        random_urls = random.sample(urls, number)

        return random_urls

    def get_last_page_number(self) -> str:
        """
        This method gets a last page number from a website.

        :return: last page number
        """
        last_page_number = self.soup.find('a', class_='pages__controls__last')['data-page-number']

        return last_page_number

    def get_all_advertisements_links_from_main_pages(self, forbidden_urls: list, url: str) -> list:
        """
        This method gets the right URLs from the main pages.

        :param forbidden_urls: list of URLs to pass
        :param url: current main page URL
        :return: list of the right URLs
        """
        urls = list()

        while url not in forbidden_urls:
            for url in self.soup.findAll('a', class_='list__item__content__title__name link'):
                urls.append(url['href'])

            return urls

        return urls

    def get_category_of_advertisement(self) -> dict:
        """
        This method gets a category of advertisement.

        :return: dictionary with a category.
        """
        advertise_category: str = 'None'

        for z in self.soup.findAll('span', itemprop='name')[-1]:
            advertise_category: str = unidecode(z)
        self.advert_details['Advert_category'] = advertise_category

        return self.advert_details

    def get_advert_title(self) -> dict:
        """
        This method gets title of advertisement.

        :return: updated dictionary with a title
        """
        advert_title: str = unidecode(self.soup.find('h1', class_='title').text)
        self.advert_details['Title'] = advert_title

        return self.advert_details

    def get_advert_link(self, url: str) -> dict:
        """
        This method gets a URL of an advertisement and place it into a dictionary for committing to a database.

        :param url: advertise URL
        :return: updated dictionary with a URL
        """
        advert_link: str = url
        self.advert_details['Url'] = advert_link

        return self.advert_details

    def get_core_details(self) -> dict:
        """
        This method gets full particulars from advertisements.

        :return: dictionary with advertisement details
        """
        for item in self.soup.findAll('div', class_='oglDetails panel'):
            for container in item.findAll('div', class_='oglField__container'):

                name = container.find('div', class_='oglField__name')
                value = container.find('span', class_='oglField__value')
                for_sibling = container.find('div', class_='oglField__name')

                if not name.find('span', class_='NewPrice__value'):
                    name = unidecode(name.get_text())
                elif name.find('span', class_='NewPrice__value'):
                    name = 'Cena'

                self.advert_details[name] = value
                '''
                First part address value filter. (City and district)
                '''
                if value is None:
                    value = for_sibling.next_sibling
                    self.advert_details[name] = unidecode(str(value).replace('\xa0', ' '))

                    '''
                    Second address value filter. (Street and number of flat)
                    There is a solved problem between the price and address fields.
                    '''
                    if for_sibling.find_next_sibling('br'):
                        value = for_sibling.find_next_sibling().next_sibling
                        self.advert_details[name] += ' ' + unidecode(str(value).replace('\xa0', ''))

                if name == 'Dodatkowe informacje':
                    value = [
                        unidecode(i)
                        for value in container.findAll('ul', class_='oglFieldList')
                        for i in value.get_text().split('\n') if i
                    ]

                    self.advert_details[name] = ', '.join(item for item in value)

                if isinstance(value, str):
                    continue

                if not isinstance(value, list):
                    value = unidecode(value.get_text())
                    self.advert_details[name] = value

        if self.advert_details['Adres'] is None:
            rent__panel_address = self.soup.find('div', class_='oglField oglField--address')
            address = rent__panel_address.find('div', class_='oglField__name').next_sibling
            for_sibling = rent__panel_address.find('div', class_='oglField__name')

            if for_sibling.find_next_sibling('br'):
                address += ' ' + for_sibling.find_next_sibling().next_sibling
            self.advert_details['Adres'] = unidecode(address.replace('\xa0', ' '))

        return self.advert_details

    def get_advert_stats(self) -> dict:
        """
        This method gets advertisement statistic information.

        :return: dictionary with advert statistic information
        """
        tag = self.soup.find('ul', class_='oglStats')

        for stats in tag.findAll('li'):
            name = unidecode(str(stats.find('span').previous_element).rstrip(': '))
            value = unidecode(stats.find('span').get_text(strip=True))
            self.advert_stats[name] = value

        return self.advert_stats

    def get_advert_description(self) -> dict:
        """
        This method gets advertise description written by advertiser. This description will be analise in the another
        application.

        :return: dictionary with advert description
        """
        description = self.soup.find('div', class_='ogl__description').get_text(strip=True)
        self.advert_details['Description'] = description

        return self.advert_details
