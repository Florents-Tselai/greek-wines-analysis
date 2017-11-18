from time import time
import pandas as pd
import json
from houseofwine_gr import scraper
import os
import errno


def main():
    try:
        os.makedirs('./data')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    wines = scraper.HouseOfWineScraper().wines()
    f_name = 'houseofwine.gr-wines'
    with open('./data/{}.json'.format(f_name), 'w', encoding='utf-8') as f:
        json.dump(wines, f, ensure_ascii=False, indent=4, sort_keys=True)

    pd.DataFrame(wines).set_index('name').to_excel('./data/{}.xlsx'.format(f_name))
    pd.DataFrame(wines).set_index('name').to_csv('./data/{}.csv'.format(f_name))


if __name__ == '__main__':
    main()