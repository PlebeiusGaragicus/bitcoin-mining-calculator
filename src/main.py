# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This is the main module that you run
"""

import sys
import threading
import logging

from pywebio import pin
from pywebio import output
from pywebio import session
from pywebio import start_server

from constants import *
from nodes import *
from popups import *
from data import *
from webio import *
from calcs import *

def download_bitcoin_network_data():
    """
        This tries to get the latest bitcoin network data + price
    """

    p = get_price()

    if p == -1:
        logging.error("Unable to get current bitcoin price")
        p = popup_get_price_from_user()

        logging.info(f"Using user-supplied Bitcoin price: ${p:,.2f}")
    else:
        logging.info(f"Bitcoin price: ${p:,.2f}")

    pin.pin[PIN_BTC_PRICE_NOW] = p
    pin.pin[PIN_BOUGHTATPRICE] = p

    load_success = False
    path = useful_node()
    if path != None:
        load_success = get_stats_from_node(path)

    if not load_success:
        if not get_stats_from_luxor():
            if not get_stats_from_internet():
                if not popup_get_stats_from_user():
                    output.toast("Unable to get bitcoin network status")

#################
def cleanup():
    logging.info("The web page was closed - goodbye")
    exit(0)

###############################
def main():
    session.set_env(title="bitcoin mining profit calculator")

    t = threading.Thread(target=session.hold)
    session.register_thread( t )
    t.start()
    session.defer_call(cleanup)

    show_user_interface_elements()
    download_bitcoin_network_data()

    # TODO DEBUG ONLY
    pin.pin[PIN_WATTAGE] = 3050
    pin.pin[PIN_HASHRATE] = 90
    pin.pin[PIN_COST] = 5375
    pin.pin[PIN_BOUGHTATPRICE] = 29500

#############################
if __name__ == '__main__':

    logginglevel = logging.INFO
    server = True
    # we use a slice to skip argv[0] which is the path to this script
    for arg in sys.argv[1:]:
        found = False
        if arg == '--help' or arg == '-h':
            print(CLI_HELP)
            exit(0)
        if arg == '--debug':
            found = True
            logginglevel = logging.DEBUG
        if found == False:
            print(f"unknown parameter: {arg}\n")
            print(CLI_HELP)
            exit(1)

    logging.basicConfig(
        level=logginglevel,
        format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler('debug.log', mode='w')])

    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open
    # Also, this script won't exit when you close the webpage otherwise - probably something to do with the thread running session.hold()
    start_server(main, port=8080, debug=True)
