# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This is the main module that you run
"""

import sys, getopt
import threading
import logging

from pywebio import pin
from pywebio import output
from pywebio import session
from pywebio import start_server

from constants import *
import config
from data import get_price, get_stats_from_internet
from node import useful_node, get_stats_from_node
from popups import popup_get_price_from_user, popup_get_stats_from_user
from webio import show_user_interface_elements, update_numbers

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

    pin.pin[PIN_BTC_PRICE_NOW] = pin.pin[PIN_BOUGHTATPRICE] = p

    load_success = False
    config.node_path = useful_node()
    if config.node_path != None:
        load_success = get_stats_from_node(config.node_path)

    if not load_success:
        #if not get_stats_from_luxor():
        if not get_stats_from_internet():
            if not popup_get_stats_from_user():
                output.toast("Unable to get bitcoin network status")

##################################
def enter_debug_values() -> None:
    pin.pin[PIN_WATTAGE] = 3050
    pin.pin[PIN_COST] = 5375
    pin.pin[PIN_HASHRATE] = 90

#################
def cleanup():
    logging.info("The web page was closed - goodbye")
    exit(0)

###############################
def main():
    session.set_env(title="bitcoin mining profit calculator")

    t = threading.Thread(group=None, target=session.hold)
    session.register_thread( t )
    t.start()
    session.defer_call(cleanup)

    show_user_interface_elements()
    download_bitcoin_network_data()
    enter_debug_values()
    update_numbers() # this is the callback function used to ensure all UI read_only fields are updated

    # TODO DEBUG ONLY
    if "--debug" in sys.argv:
        pin.pin[PIN_WATTAGE] = 3050
        pin.pin[PIN_HASHRATE] = 90
        pin.pin[PIN_COST] = 5375
        pin.pin[PIN_BOUGHTATPRICE] = 29500

#############################
if __name__ == '__main__':

    # server = True
    # # we use a slice to skip argv[0] which is the path to this script
    # for arg in sys.argv[1:]:
    #     found = False
    #     if arg == '--help' or arg == '-h':
    #         print(CLI_HELP)
    #         exit(0)
    #     if arg == '--debug':
    #         found = True
    #         logginglevel = logging.DEBUG
    #     if arg == '--key':
    #         apikey = 
    #     if found == False:
    #         print(f"unknown parameter: {arg}\n")
    #         print(CLI_HELP)
    #         exit(1)

    logginglevel = logging.INFO
    try:
      opts, args = getopt.getopt(args=sys.argv[1:], shortopts="hdk:", longopts=['help', 'debug', 'key='])
    except getopt.GetoptError as err:
        #logging.exception(err) # can't use this becuase basicConfig has not been called yet!!!
        print(err)
        print(CLI_USAGE_HELP)
        exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(CLI_USAGE_HELP)
            exit(1)
        elif opt in ("-d", "--debug"):
            logginglevel = logging.DEBUG
        elif opt in ("-k", "--key"):
            config.apikey = arg

    logging.basicConfig(
        level=logginglevel,
        format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler('debug.log', mode='w')])

    logging.debug(f"Luxor API key: {config.apikey}")

    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open
    # Also, this script won't exit when you close the webpage otherwise - probably something to do with the thread running session.hold()
    start_server(main, port=8080, debug=True)
