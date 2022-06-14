# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import logging
import json
import urllib.request as ur

from pywebio import pin
from pywebio import output

from constants import *

def get_difficulty(bits: int):
    """
        This converts the 'bits' field in a bitcoin block to the 'difficulty' number

        Taken (AKA, shamelessly plagiarized) from bitcoin core:
            https://github.com/bitcoin/bitcoin/blob/8f3ab9a1b12a967cd9827675e9fce112e51d42d8/src/rpc/blockchain.cpp#L75-L95
        Also helpful:
            https://en.bitcoin.it/wiki/Difficulty
            https://stackoverflow.com/a/22161019
            https://bitcoin.stackexchange.com/questions/30467/what-are-the-equations-to-convert-between-bits-and-difficulty
            https://bitcointalk.org/index.php?topic=192886.0

        ...or just use this shell script     ¯\_(ツ)_/¯
        #!/bin/bash
        echo "ibase=16;FFFF0000000000000000000000000000000000000000000000000000 / $1" | bc -l
    """

    shift = (bits >> 24) & 0xFF
    diff = 0x0000FFFF / (bits & 0x00FFFFFF)

    while shift < 29:
        diff *= 256.0
        shift += 1
    
    while shift > 29:
        diff /= 256.0
        shift -= 1

    return diff



# https://bitcoin.stackexchange.com/questions/5556/relationship-between-hash-rate-and-difficulty

# https://minerdaily.com/2021/how-are-bitcoins-difficulty-and-hash-rate-calculated/


#blockheight = int(str(ur.urlopen(ur.Request(f'https://blockchain.info/rawblock/{latest_hash}')).read()).split('"height":')[1].split(',')[0])

nBlocks = BLOCKS_PER_EPOCH
latest_hash = str(ur.urlopen(ur.Request('https://blockchain.info/q/latesthash')).read(),'utf-8')
block = str(ur.urlopen(ur.Request(f'https://blockchain.info/rawblock/{latest_hash}')).read())



# ##########################################
# def get_stats_from_internet() -> bool:
#     """
#         This gets the needed bitcoin network data from blockchain.info :)
#         https://www.blockchain.com/api/q
#     """

#     try:
#         h = int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read())
#         #d = int(float(ur.urlopen(ur.Request('https://blockchain.info/q/getdifficulty')).read()))
#         nh = int(ur.urlopen(ur.Request('https://blockchain.info/q/hashrate')).read()) / 1000
#         p = get_price() #query_bitcoinprice() #int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))

#         f = get_average_block_fee_from_internet()
#         logging.debug(f"fee: {f}")
#     except Exception as e:
#         logging.debug("", exc_info=True)
#         output.toast("Could not download network status.", color='error', duration=4)
#         return False

#     pin.pin[PIN_BTC_PRICE_NOW] = p
#     pin.pin[PIN_BOUGHTATPRICE] = p
#     pin.pin[PIN_HEIGHT] = h
#     pin.pin[PIN_AVERAGEFEE] = f
#     pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
#     pin.pin[PIN_NETWORKHASHRATE] = nh

#     return True