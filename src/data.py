# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This module gets bitcoin network data from the internets if you don't have a bitcoin archive node.
"""

import requests
#import datetime
import logging
import json
import urllib.request as ur

from pywebio import pin
from pywebio import output

import pandas as pd

import config
import constants as c
from calcs import get_hashrate_from_difficulty
from luxor import LuxorAPI, LUXOR_ENDPOINT
import node
import popups

# try:
#     # keep it secret... keep it safe
#     import apikey
#     API_KEY = apikey.LUXOR_API_KEY
# except ModuleNotFoundError as e:
#     API_KEY = None
#     # we don't want to use the logging module here because it will init and run basicConfig()
#     # we don't want that becuase you can only run basicConfig once and we do that in main()
#     print("You don't seem to have a LUXOR api key.  That's ok")

def download_bitcoin_network_data():
    """
        This tries to get the latest bitcoin network data + price
    """

    p = get_price()

    if p == -1:
        logging.error("Unable to get current bitcoin price")
        p = popups.popup_get_price_from_user()

        logging.info(f"Using user-supplied Bitcoin price: ${p:,.2f}")
    else:
        logging.info(f"Bitcoin price: ${p:,.2f}")

    pin.pin[c.PIN_BTC_PRICE_NOW] = pin.pin[c.PIN_BOUGHTATPRICE] = p

    if not node.get_stats_from_node():
        logging.debug("unable to get stats from node...")
        #if not get_stats_from_luxor():
        if not get_stats_from_internet():
            if not popups.popup_get_stats_from_user():
                output.toast("Unable to get bitcoin network status")

########################################
# https://github.com/LuxorLabs/hashrateindex-api-python-client
def get_stats_from_luxor() -> bool:
    """
        This gets the needed bitcoin network data from Luxor's beautiful API
    """
    if config.apikey == None:
        output.toast("Luxor API key is not supplied", color='error')
        return

    output.toast("Gathering data from luxor...", duration=2)

    lux = LuxorAPI(host=LUXOR_ENDPOINT, method='POST', key=config.apikey)
# [{'timestamp': '2022-06-09T02:34:43+00:00',
# 'hashpriceUsd': '0.1264933082578627',
# 'networkHashrate7D': '222015523.66824248',
# 'networkDiff': '30283293547736',
# 'estDiffAdj': '20.24',
# 'coinbaseRewards24H': '6.31113782730337',
# 'feesBlocks24H': '0.9782052368539326',
# 'marketcap': '575.5891660946875',
# 'nextHalvingCount': 100015,
# 'nextHalvingDate': '2024-05-03T00:00:00+00:00',
# 'txRateAvg7D': '2.8970980756008053'}]

    try:
        data = lux.get_bitcoin_overview()['data']['bitcoinOverviews']['nodes']

        diff = data['networkDiff']
        #nh = lux.get_network_hashrate("_7_DAY")['data']['getNetworkHashrate']['nodes']
        nh = round(get_hashrate_from_difficulty(diff), 2)

        #price = lux.get_ohlc_prices("_1_DAY")['data']['getChartBySlug']['data']

        output.toast("loading complete!!!", color='success')
    except Exception as e:
        logging.exception('')
        output.toast("Could not download network status.", color='error', duration=4)
        return False

    pin.pin[c.PIN_HEIGHT] = 0 # luxor does not provide the height
    pin.pin[c.PIN_NETWORKHASHRATE] = f"{nh:,} TH/s"
    #pin.pin[PIN_NETWORKHASHRATE] = 0
    #pin.pin[PIN_AVERAGEFEE] = 0
    #pin.pin[PIN_BOUGHTATPRICE] = 0
    #pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")

    return True

#############################
def get_luxor_price_as_df():
    """
        I couldn't tell you what a data frame is.. but this function returns one
        returns None on error
    """
    if config.apikey == None:
        output.toast("Luxor API key is not supplied", color='error')
        return

    try:
        lux = LuxorAPI(host=LUXOR_ENDPOINT, method='POST', key=config.apikey)

        price = lux.get_ohlc_prices("ALL")['data']['getChartBySlug']['data']
        pdf = pd.DataFrame(price)

        pdf.to_csv('luxor_price_data_all.csv', )
        pdf.to_csv()
    except Exception:
        logging.debug("", exc_info=True)
        return None

    return pdf

########################################
def get_stats_from_internet() -> bool:
    """
        This gets the needed bitcoin network data from blockchain.info :)
        https://www.blockchain.com/api/q
    """

    try:
        h = int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read())
        diff = int(float(ur.urlopen(ur.Request('https://blockchain.info/q/getdifficulty')).read()))
        #nh = int(ur.urlopen(ur.Request('https://blockchain.info/q/hashrate')).read()) / 1000
        #p = get_price() #query_bitcoinprice() #int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))

        #nh = round((diff * 2 ** 32) / 600 / TERAHASH, 2)
        nh = round(get_hashrate_from_difficulty(diff), 2)

        #f = get_average_block_fee_from_internet()
    except Exception as e:
        logging.debug("", exc_info=True)
        output.toast("Could not download network status.", color='error', duration=4)
        return False

    config.height = h
    config.difficulty = diff
    # pin.pin[PIN_BTC_PRICE_NOW] = p
    # pin.pin[PIN_BOUGHTATPRICE] = p
    pin.pin[c.PIN_HEIGHT] = h
    #pin.pin[PIN_AVERAGEFEE] = f
    #pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
    pin.pin[c.PIN_NETWORKDIFFICULTY] = diff
    pin.pin[c.PIN_NETWORKHASHRATE] = f"{nh:,} TH/s"
    pin.pin_update(c.PIN_NETWORKHASHRATE, help_text=f"{nh/c.MEGAHASH:.2f} EH/s")

    return True

########################################
# https://www.blockchain.com/api/blockchain_api
# https://blockchain.info/rawblock/<block_hash> _OR_ https://blockchain.info/rawblock/<block_hash>?format=hex
# TODO I think we are off by one during countdown
def get_average_block_fee_from_internet(nBlocks = c.EXPECTED_BLOCKS_PER_DAY) -> float:
    try:
        latest_hash = str(ur.urlopen(ur.Request('https://blockchain.info/q/latesthash')).read(),'utf-8')
        blockheight = int(str(ur.urlopen(ur.Request(f'https://blockchain.info/rawblock/{latest_hash}')).read()).split('"height":')[1].split(',')[0])
    except ur.HTTPError as e:
        logging.exception('')
        return -1

    with output.popup(f"Averaging transactions fees for last {nBlocks} blocks...", closable=False) as p:
        pin.put_input("remaining", value=nBlocks, label="Blocks remaining:")
        pin.put_textarea("feescroller", value='')
        pin.put_input('sofar', value='', label="Average so far:")
        output.put_button("Stop early", color='danger', onclick=lambda: output.close_popup())

        total_fee = 0
        for bdx in range(blockheight-nBlocks, blockheight):
            try:
                block_data = str(ur.urlopen(ur.Request(f'https://blockchain.info/rawblock/{latest_hash}')).read())
            except ur.HTTPError as e:
                logging.exception('HTTPError')
                return -1

            block_fee = int(block_data.split('"fee":')[1].split(',')[0])
            total_fee += block_fee

            pin.pin['remaining'] = blockheight - bdx
            pin.pin['sofar'] = f"{ (total_fee / (1 + bdx - blockheight + nBlocks)) :,.2f}"

            block_height = int(block_data.split('"block_index":')[1].split(',')[0])
            latest_hash = block_data.split('"prev_block":')[1].split(',')[0].strip('"')

            try:
                pin.pin['feescroller'] = f"block: {bdx} --> fee: {block_fee:,}\n" + pin.pin["feescroller"]
            except TypeError as e:
                # this error happens if the popup was closed
                logging.debug("This error is expected if you push the 'stop early' button", exc_info=True)
                return round(total_fee / (1 + bdx - block_height + nBlocks), 2)
            logging.debug(f"block: {bdx} -->  fee: {format(block_fee, ',').rjust(11)} satoshi")

    output.close_popup()

    total_fee /= nBlocks
    logging.debug(f"Average fee per block in last {nBlocks} blocks: {total_fee:,.0f}")
    return round(total_fee, 2)

############################
def get_price() -> float:
    """
        This will return the price of bitcoin, first using luxor api and then coinbase on failure
        Returns -1 on error
    """
    logging.debug("Getting price of bitcoin...")

    #if config.apikey != None:
    #    p = query_bitcoinprice_luxor()
    #else:
    p = query_bitcoinprice_coinbase()

    if p == -1 or p == None:
        logging.warn("Unable to get the price of bitcoin")
        output.toast("Unable to get the price of bitcoin", color='error')
        #p = query_bitcoinprice_coinbase()
    
    config.price = round(p, 2)

    return round(p, 2)

########################################
def query_bitcoinprice_luxor() -> float:
    """
        Returns the current bitcoin price for Luxor's API
        Returns -1 on error
    """

    if config.apikey == None:
        output.toast("Luxor API key is not supplied", color='error')
        return

    try:
        lux = LuxorAPI(host=LUXOR_ENDPOINT, method='POST', key=config.apikey)
        price = lux.get_ohlc_prices("_1_DAY")['data']['getChartBySlug']['data']

        # luxor's "_1_DAY" returns a bunch of data... the whole day's worth of price data every 15 minutes...
        # so let's just take the first and last price and average them, shall we?
        avg = (price[1]['open'] + price[-1]['open']) / 2
    except Exception as e:
        logging.debug(f"__func__ exception", exc_info=True)
        # TODO return None instead on error
        return -1

    return avg

##################################
def query_bitcoinprice_coinbase() -> float:
    """
        queries the current bitcoin price from the coindesk.com API
        returns (-1) on error
        shell one-liner:
            - alias btcprice = "curl -s 'https://api.coinbase.com/v2/prices/spot?currency=USD' | jq -r '.data.amount'"
    """

    try:
        API_URL = 'https://api.coinbase.com/v2/prices/spot?currency=USD'
        response = ur.urlopen(ur.Request( API_URL )).read()
        data = json.loads(response) # returns dict
        price = float( data['data']['amount'] )
    except Exception as e:
        logging.debug(f"__func__ exception", exc_info=True)
        # TODO return None instead on error
        return -1

    return price





# FOR HELP WITH UNIX TIME
# https://www.unixtimestamp.com/index.php

def coinbase_fetch_price_history(start_timestamp: int, end_timestamp: int) -> pd.DataFrame:
    """
        refer to: https://docs.cloud.coinbase.com/exchange/reference/exchangerestapi_getproductcandles
        code example taken from: https://www.cryptodatadownload.com/blog/posts/Use-Python-to-Download-Coinbase-Price-Data/
    """

    logging.debug(f"getting coinbase price history {start_timestamp=} {end_timestamp=}")
    SYMBOL = 'BTC-USD'
    COINBASE_URL = f'https://api.pro.coinbase.com/products/{SYMBOL}/candles?granularity=86400&start={start_timestamp}&end={end_timestamp}'
    response = requests.get(COINBASE_URL)

    logging.debug(f"{response.status_code=}")
    if response.status_code == 200:
        data = pd.DataFrame(json.loads(response.text), columns=['unix', 'low', 'high', 'open', 'close', 'volume'])
        #data = pd.DataFrame(json.loads(response.text), columns=['unix', 'close'])
        #data = pd.DataFrame(json.loads(response.text))
        data['date'] = pd.to_datetime(data['unix'], unit='s')  # convert to a readable date
        #data['unix'] = pd.to_datetime(data['unix'], unit='s')  # convert to a readable date

        # if data is None:
        #     logging.error("Did not return any data from Coinbase for this symbol")
        #     return None
        # else:
        #     data.to_csv(f'Coinbase_price_data.csv', index=False)
    else:
        logging.error("Did not receieve OK response from Coinbase API")
        return None
    
    logging.debug(f"returning: {data=}")

    return data
