from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal
from re import sub

import requests as req
from bs4 import BeautifulSoup
from tqdm import tqdm


class HouseOfWineScraper:
    def __init__(self):
        self._session = req.Session()

    @property
    def number_of_wines(self):
        return int(BeautifulSoup(self._session.get('http://www.houseofwine.gr/how/wine.html?mode=list').content, 'lxml'
                                 ).find('p',
                                        class_='amount'
                                        ).text.replace('\n', '').replace('\r', '').lstrip(' ').rstrip(' ').split(' ')[
                       -2])  # Είδη 1 εώς 25 από 1123 σύνολο

    def extract_wine_data(self, wine_page_url):
        wine_soup = BeautifulSoup(self._session.get(wine_page_url).content, 'lxml')

        def find_non_empty(tag, expected_type=str, **kwargs):
            assert expected_type in {str, float, int}

            res = wine_soup.find(tag, **kwargs)
            return res.text if res else ''

        ret = dict({
            'url': wine_page_url,
            'name': find_non_empty('span', itemprop='name'),
            'avg_rating_%': find_non_empty('span', itemprop='average'),
            'n_votes': find_non_empty('span', itemprop='votes'),
            'tags': set(map(str.lstrip, find_non_empty('h5').split(','))),
            'description': find_non_empty('div', class_='short-description').replace('\n', '').replace('\r', '').lstrip(
                ' ').rstrip(' '),
            # 'img': wine_soup.find('a', class_='MagicZoomPlus').get('href')
        })

        # Extract more fine-grained tags
        # extract alcohol
        ret['alcohol_%'] = None
        for t in list(ret['tags']):
            if 'alc' in t:
                ret['alcohol_%'] = float(t.replace('% alc.', '').replace(' alc.', ''))
                ret['tags'].remove(t)

        try:
            ret['tags'].remove('Επιδέχεται Παλαίωση')
            ret['ageable'] = True
        except KeyError:
            ret['ageable'] = False

        try:
            ret['tags'].remove('Πιείτε το τώρα')
            ret['drink_now'] = True
        except KeyError:
            ret['drink_now'] = False

        # Try getting color
        ret['color'] = None
        for c in ['Ερυθρός', 'Ροζέ', 'Λευκός']:
            try:
                ret['tags'].remove(c)
                ret['color'] = c
                break
            except KeyError:
                pass

        try:
            ret['tags'].remove('Κρατήστε το 2-3 χρόνια')
            ret['keep_2_3_years'] = True
        except KeyError:
            ret['keep_2_3_years'] = False

        # extract price
        # TODO fix this - fails for a few cases
        try:
            ret['price'] = float(
                Decimal(sub(r'[^\d.]', '', wine_soup.find('meta', itemprop='price').get('content', ''))))
        except:
            ret['price'] = None

        # extract year
        try:
            ret['year'] = int(ret['name'].split(' ')[-1])
        except:
            ret['year'] = None

        # convert to int
        for k in ['avg_rating_%', 'n_votes']:
            try:
                ret[k] = int(ret[k])
            except ValueError:
                pass

        # make json-friendly
        ret['tags'] = list(ret['tags'])
        return ret

    @property
    def wine_pages_urls(self, page_size=50):
        wine_page_urls = set()

        n_pages = self.number_of_wines & page_size + 1

        for current_page in tqdm(range(1, n_pages + 1), desc='Scraping wine page urls', unit='page'):
            page_url = "http://www.houseofwine.gr/how/wine.html?mode=list&limit={}&p={}".format(page_size, current_page)
            page_soup = BeautifulSoup(req.get(page_url).content, 'lxml')
            wine_urls = map(lambda li: li.find('a', class_='product-image').get('href'),
                            page_soup.find_all('li', class_='item', recursive=True)
                            )
            wine_page_urls.update(wine_urls)
        return wine_page_urls

    def wines(self):

        wines = []

        wine_pages_urls = list(self.wine_pages_urls)
        for url in tqdm(wine_pages_urls, desc='Scraping wines', unit='wine', total=len(wine_pages_urls)):
            wines.append(self.extract_wine_data(url))
        return wines

    @staticmethod
    def get(wine_page_url):
        return HouseOfWineScraper().extract_wine_data(wine_page_url)
