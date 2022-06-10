import logging

import json
import urllib.request as ur

from pywebio import pin
from pywebio import output

import pandas as pd

from luxor_api import API
# keep it secret... keep it safe
import apikey

from constants import *

########################################
# https://github.com/LuxorLabs/hashrateindex-api-python-client
def get_stats_from_luxor() -> bool:
    output.toast("Gathering data from luxor...", duration=2)

    ENDPOINT = 'https://api.hashrateindex.com/graphql'
    lux = API(host=ENDPOINT, method='POST', key=apikey.LUXOR_API_KEY)

    try:
        data = lux.get_bitcoin_overview()['data']['bitcoinOverviews']['nodes']
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

        nh = lux.get_network_hashrate("_7_DAY")['data']['getNetworkHashrate']['nodes']

        price = lux.get_ohlc_prices("_1_DAY")['data']['getChartBySlug']['data']

        return False # TODO DEBUG ONLY
        
        output.toast("loading complete!!!", color='success')
    except Exception as e:
        logging.exception('')
        output.toast("Could not download network status.", color='error', duration=4)
        return False

    pin.pin[PIN_BTC_PRICE_NOW] = 0
    pin.pin[PIN_BOUGHTATPRICE] = 0
    pin.pin[PIN_HEIGHT] = 0
    pin.pin[PIN_AVERAGEFEE] = 0
    #pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
    pin.pin[PIN_NETWORKHASHRATE] = 0

    return True



def get_luxor_price_as_df():
    """
        returns None on error
    """
    ENDPOINT = 'https://api.hashrateindex.com/graphql'
    lux = API(host=ENDPOINT, method='POST', key=apikey.LUXOR_API_KEY)

    try:
        price = lux.get_ohlc_prices("ALL")['data']['getChartBySlug']['data']
        pdf = pd.DataFrame(price)
    except Exception as e:
        logging.exception('')
        return None

    return pdf

########################################
def get_stats_from_internet() -> bool:
    """
        https://www.blockchain.com/api/q
    """
    output.put_text("Gathering data from blockchain.info...", scope='init')

    try:
        h = int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read())
        #d = int(float(ur.urlopen(ur.Request('https://blockchain.info/q/getdifficulty')).read()))
        nh = int(ur.urlopen(ur.Request('https://blockchain.info/q/hashrate')).read()) / 1000
        p = get_price() #query_bitcoinprice() #int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))

        f = get_average_block_fee_from_internet()
        logging.debug(f"fee: {f}")
    except Exception as e:
        logging.exception('')
        output.toast("Could not download network status.", color='error', duration=4)
        return False

    pin.pin[PIN_BTC_PRICE_NOW] = p
    pin.pin[PIN_BOUGHTATPRICE] = p
    pin.pin[PIN_HEIGHT] = h
    pin.pin[PIN_AVERAGEFEE] = f
    pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
    pin.pin[PIN_NETWORKHASHRATE] = nh

    return True



########################################
# https://www.blockchain.com/api/blockchain_api
# https://blockchain.info/rawblock/<block_hash> _OR_ https://blockchain.info/rawblock/<block_hash>?format=hex
# TODO I think we are off by one during countdown
def get_average_block_fee_from_internet(nBlocks = EXPECTED_BLOCKS_PER_DAY) -> int:
    # TODO - USE A TRY EXCEPT BLOCK... OR ELSE FUCK FUCK FUCK.. ALSO JUST RETURN 0 AND ALERT THE USER WITH OUTPUT.TOAST
    latest_hash = str(ur.urlopen(ur.Request('https://blockchain.info/q/latesthash')).read(),'utf-8')
    blockheight = int(str(ur.urlopen(ur.Request(f'https://blockchain.info/rawblock/{latest_hash}')).read()).split('"height":')[1].split(',')[0])

    with output.popup(f"Averaging transactions fees for last {nBlocks} blocks...", closable=False) as p:
        pin.put_input("remaining", value=nBlocks, label="Blocks remaining:")
        pin.put_textarea("feescroller", value='')
        pin.put_input('sofar', value='', label="Average so far:")
        output.put_button("Stop early", color='danger', onclick=lambda: output.close_popup())

        total_fee = 0
        for bdx in range(blockheight-nBlocks, blockheight):
            block_data = str(ur.urlopen(ur.Request(f'https://blockchain.info/rawblock/{latest_hash}')).read())
            block_fee = int(block_data.split('"fee":')[1].split(',')[0])
            total_fee += block_fee

            pin.pin['remaining'] = blockheight - bdx
            pin.pin['sofar'] = f"{ (total_fee / (1 + bdx - blockheight + nBlocks)) :,.2f}"

            block_height = int(block_data.split('"block_index":')[1].split(',')[0])
            latest_hash = block_data.split('"prev_block":')[1].split(',')[0].strip('"')

            try:
                pin.pin['feescroller'] = f"block: {bdx} --> fee: {block_fee:,}\n" + pin.pin["feescroller"]
            except Exception as e:
                logging.exception('')
                # this error happens if the popup was closed
                return round(total_fee / (1 + bdx - block_height + nBlocks), 2)
            logging.debug(f"block: {bdx} -->  fee: {format(block_fee, ',').rjust(11)} satoshi")

    output.close_popup()

    total_fee /= nBlocks
    logging.debug(f"Average fee per block in last {nBlocks} blocks: {total_fee:,.0f}")
    return round(total_fee, 2)






############################
def get_price() -> float:
    logging.debug("Getting price of bitcoin...")
    p = query_bitcoinprice_luxor()

    if p == -1:
        p = query_bitcoinprice_coinbase()
    
    if p == -1:
        return -1
    else:
        return p






########################################
def query_bitcoinprice_luxor() -> float:
    """
        returns -1 on error
    """
    try:
        ENDPOINT = 'https://api.hashrateindex.com/graphql'
        lux = API(host=ENDPOINT, method='POST', key=apikey.LUXOR_API_KEY)
        price = lux.get_ohlc_prices("_1_DAY")['data']['getChartBySlug']['data']

        # luxor's "_1_DAY" returns a bunch of data... the whole day's worth of price data every 15 minutes...
        # so let's just take the first and last price and average them, shall we?
        avg = (price[1]['open'] + price[-1]['open']) / 2
    except Exception as e:
        logging.exception('')
        return -1

    return avg

##################################
def query_bitcoinprice_coinbase() -> float:
    """
        - queries the current bitcoin price from the coindesk.com API

        - returns (-1) on error

        - shell one-liner:
            - alias btcprice = "curl -s 'https://api.coinbase.com/v2/prices/spot?currency=USD' | jq -r '.data.amount'"
    """

    try:
        API_URL = 'https://api.coinbase.com/v2/prices/spot?currency=USD'
        response = ur.urlopen(ur.Request( API_URL )).read()
        data = json.loads(response) # returns dict
        price = float( data['data']['amount'] )
    except Exception as e:
        logging.exception('')
        return -1

    return price
