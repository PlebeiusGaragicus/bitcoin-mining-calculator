import logging

from luxor_api import API
# keep it secret... keep it safe
import apikey


def query_bitcoinprice_luxor():
    try:
        ENDPOINT = 'https://api.hashrateindex.com/graphql'
        lux = API(host=ENDPOINT, method='POST', key=apikey.LUXOR_API_KEY)
        price = lux.get_ohlc_prices("_1_DAY")['data']['getChartBySlug']['data']

        avg = (price[1]['open'] + price[-1]['open']) / 2
    except Exception as e:
        logging.exception('')
        return -1

    return avg
