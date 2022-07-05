import logging

from btc_mining_calcs.luxor import LuxorAPI, LUXOR_ENDPOINT
# keep it secret... keep it safe
import apikey


def query_bitcoinprice_luxor():
    try:
        lux = LuxorAPI(host=LUXOR_ENDPOINT, method='POST', key=apikey.LUXOR_API_KEY)
        price = lux.get_ohlc_prices("_1_DAY")['data']['getChartBySlug']['data']

        avg = (price[1]['open'] + price[-1]['open']) / 2
    except Exception as e:
        logging.debug("", exc_info=True)
        return -1

    return avg
