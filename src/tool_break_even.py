# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This is a tool that calculates the break-even of price, cost/kWh and network hashrate
"""

import threading

from pywebio import pin
from pywebio import output
from pywebio import session
from pywebio import start_server

import urllib.request as ur

from constants import *
from node import *
from data import *
from calcs import *

def update_break_even( callback_throwaway ):
    """
        This call back is used for every onchange= 'pin' input field.
        We just continuously update the numbers on every keyboard stroke
    """
    try:
        wattage = int(pin.pin['wattage'])
        hashrate = float(pin.pin['hashrate'])
        poolfee = float(pin.pin['poolfee']) / 100

        height = int(pin.pin['height'])
        blocktxfee = float(pin.pin['blocktxfee'])

        rate = float(pin.pin['rate'])
        nh = float(pin.pin['nh'])
        price = float(pin.pin['price'])
    except Exception as e:
        print("Exception:", e)
        return
    
    if rate == 0:
        print("cost / kWh is 0 ...")
        return

    price_satoshi = price / ONE_HUNDRED_MILLION

    reward = block_subsity(height) + blocktxfee
    be_nh = (reward * hashrate * (1 - poolfee) * price_satoshi * 6000) / (rate * wattage)
    be_p = ONE_HUNDRED_MILLION * ((nh * rate * wattage) / (reward * hashrate * (1 - poolfee) * 6000))
    be_rate = (reward * hashrate * (1 - poolfee) * price_satoshi * 6000) / (nh * wattage)

    pin.pin_update('be_rate', value=f"{be_rate:.3f}")
    pin.pin_update('be_nh', value=f"{be_nh:,.2f}")
    pin.pin_update('be_price', value=f"{be_p:,.2f}")

def height_waschanged(h):
    pin.pin['subsidy'] = f"{block_subsity(h):,}"
    update_break_even(None)

###############
def cleanup():
    print("web page closed - goodbye")
    exit(0)

###############################
def main():
    session.set_env(title="bitcoin mining break-even calculator")

    t = threading.Thread(target=session.hold)
    session.register_thread( t )
    t.start()
    session.defer_call(cleanup)

    try:
        nh = int(ur.urlopen(ur.Request('https://blockchain.info/q/hashrate')).read()) / 1000
        height = int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read())
        price =  int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))
    except:
        output.toast("Unable to get bitcoin network stats", duration=5)
        nh = height = price = 0

    with output.use_scope('main', clear=True):
        output.put_info("Enter the details of a bitcoin miner and this will calculate the break-even price")
        output.put_table(tdata=[[
            pin.put_input(name='wattage', type='number', label="Wattage"),
            pin.put_input(name='hashrate', type='float', label="Hashrate (terahash)"),
            pin.put_input(name='poolfee', type='float', label="Pool fee %", value=0)
        ]])
        pin.pin_on_change('wattage', onchange=update_break_even)
        pin.pin_on_change('hashrate', onchange=update_break_even)
        pin.pin_on_change('fee', onchange=update_break_even)

        output.put_table(tdata=[[
            pin.put_input(name='height', type='float', label="block height", value=height),
            pin.put_input(name='subsidy', type='text', label="current block subsidy", value=f"{block_subsity(height):,}", readonly=True),
            pin.put_input(name='blocktxfee', type='float', label="Average block fees", value=9_000_000) # TODO - THIS IS MADNESS!!
        ]])
        pin.pin_on_change('height', onchange=height_waschanged)
        pin.pin_on_change('subsidy', onchange=update_break_even)
        pin.pin_on_change('blocktxfee', onchange=update_break_even)
        
        output.put_table(tdata=[[
            pin.put_input(name='rate', type='float', label="Cost / kWh", value=0.12),
            pin.put_input(name='nh', type='float', label="Network hashrate (terahash)", value=nh),
            pin.put_input(name='price', type='float', label="Bitcoin price", value=price)
        ]])
        pin.pin_on_change('rate', onchange=update_break_even)
        pin.pin_on_change('nh', onchange=update_break_even)
        pin.pin_on_change('price', onchange=update_break_even)

        output.put_markdown("---")
        output.put_text("Break even:")
        output.put_table(tdata=[[
            pin.put_input(name='be_rate', type='text', label="Cost / kWh", readonly=True),
            pin.put_input(name='be_nh', type='text', label="Network hashrate (terahash)", readonly=True),
            pin.put_input(name='be_price', type='text', label="Bitcoin price", readonly=True)
        ]])

#############################
if __name__ == '__main__':
    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open, you have to click the link
    start_server(main, port=8080, debug=True)
    #main()







# def calculate_break_even():
#     wattage = pin.pin['wattage']
#     hashrate = pin.pin['hashrate']
#     rate = pin.pin['rate']
#     fee = pin.pin['fee']
#     height = pin.pin['height']
#     nh = pin.pin['nh']
#     price = pin.pin['price']

#     subsidy = block_subsity(height)

#     fee_average = 0.09 * ONE_HUNDRED_MILLION # TODO oh dear god fix this please my head hurts make it stop oh god no
#     reward = subsidy + fee_average

#     price_satoshi = price / ONE_HUNDRED_MILLION
#     share = hashrate / nh
#     rawreward = share * reward
#     s10 = rawreward * (1 - fee)
#     value = s10 * price_satoshi

#     kWh = wattage / 6000
#     cost = rate * kWh

#     # TODO - find the break-even!

#     with output.use_scope('result', clear=True):
#         output.put_text(f"10 minute cost/earnings: cost ${cost:.2f} / earn ${value:.2f}")
