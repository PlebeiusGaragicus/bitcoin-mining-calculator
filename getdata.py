import json
import urllib.request as ur

from pywebio import pin
from pywebio import output

from constants import *


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
        p = query_bitcoinprice() #int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))

        output.put_text("Getting average block fee from internet... please wait...!!!", scope='init')
        
        if debug: # TODO DEBUG ONLY
            nblocks = 1
        else:
            nblocks = EXPECTED_BLOCKS_PER_DAY
        f = get_average_block_fee_from_internet(nBlocks=nblocks)
    except Exception as e:
        print("Exception:", e)
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
def get_average_block_fee_from_internet(nBlocks = EXPECTED_BLOCKS_PER_DAY) -> int:
    """
    """
    # TODO - USE A TRY EXCEPT BLOCK... OR ELSE FUCK FUCK FUCK.. ALSO JUST RETURN 0 AND ALERT THE USER WITH OUTPUT.TOAST
    latest_hash = str(ur.urlopen(ur.Request('https://blockchain.info/q/latesthash')).read(),'utf-8')
    total_fee = 0
    for _ in range(0, nBlocks):
        block_data = str(ur.urlopen(ur.Request(f'https://blockchain.info/rawblock/{latest_hash}')).read())
        block_fee = int(block_data.split('"fee":')[1].split(',')[0])
        height = int(block_data.split('"height":')[1].split(',')[0])
        total_fee += block_fee
        #output.put_markdown(f"```block: {height} --> fee: {block_fee:,}```", scope='init')
        block_height = int(block_data.split('"block_index":')[1].split(',')[0])
        latest_hash = block_data.split('"prev_block":')[1].split(',')[0].strip('"')
        print("block: ", block_height, " -->  fee: ", format(block_fee, ',').rjust(11), " satoshi")

    total_fee /= nBlocks
    print(f"Average fee per block in last {nBlocks} blocks:", f'{total_fee:,.0f}')
    return total_fee



########################################
#API_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'
# float( data['bpi']['USD']['rate_float'] )
#price = float( data["data"]["amount"].split(".")[0].replace(',', '') )
#price = data["data"]["amount"].replace(',', '')
def query_bitcoinprice() -> float:
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
        print("Exception:", e)
        return -1

    return price



