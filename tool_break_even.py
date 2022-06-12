# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This is a tool that calculates the break-even price given miner/network stats
"""

import threading
import logging

from pywebio import pin
from pywebio import output
from pywebio import session
from pywebio import start_server

import urllib.request as ur

from constants import *
from nodes import *
from data import *
from calcs import *

def calculate_break_even():
    wattage = pin.pin['wattage']
    hashrate = pin.pin['hashrate']
    rate = pin.pin['rate']
    fee = pin.pin['fee']
    height = pin.pin['height']
    nh = pin.pin['nh']
    price = pin.pin['price']
    
    # if pin.pin['fee'] < 1:
    #     output.toast("Use whole number percents for pool fee - (Example: 2 instead of 0.02)", duration=7)

    block_reward = 50 * ONE_HUNDRED_MILLION
    block_reward >>= height // SUBSIDY_HALVING_INTERVAL

    fee_average = 0.09 * ONE_HUNDRED_MILLION # TODO oh dear god fix this please my head hurts make it stop oh god no
    reward = block_reward + fee_average

    price_satoshi = price / ONE_HUNDRED_MILLION
    share = hashrate / nh
    rawreward = share * reward
    s10 = rawreward * (1 - fee)
    value = s10 * price_satoshi

    kWh = wattage / 6000
    cost = rate * kWh

    # TODO - find the break-even!

    with output.use_scope('result', clear=True):
        output.put_text(f"10 minute cost/earnings: cost ${cost:.2f} / earn ${value:.2f}")

###############
def cleanup():
    logging.info("The web page was closed - goodbye")
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
            pin.put_input(name='rate', type='float', label="Cost / kWh"),
            pin.put_input(name='fee', type='float', label="Pool fee %", value=0)
        ],[
            pin.put_input(name='height', type='float', label="block height", value=height),
            pin.put_input(name='nh', type='float', label="Network hashrate (terahash)", value=nh),
            pin.put_input(name='price', type='float', label="Bitcoin price", value=price),
            pin.put_input(name='txfee', type='float', label="Average block fees", value=9_000_000) # TODO - THIS IS MADNESS!!
        ]])
        output.put_button("find break-even price", onclick=calculate_break_even, color='info')

#############################
if __name__ == '__main__':
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s",
    #     handlers=[logging.StreamHandler(),
    #               logging.FileHandler('debug.log', mode='w')])

    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open, you have to click the link
    start_server(main, port=8080, debug=True)
    #main()
