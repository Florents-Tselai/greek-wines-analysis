__all__ = ['scraper', 'dump']

from houseofwine_gr.scraper import HouseOfWineScraper


def get(wine_page_url):
    return HouseOfWineScraper().extract_wine_data(wine_page_url)