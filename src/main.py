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
import webio

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

    webio.show_user_interface_elements()
    webio.refresh()

#############################
if __name__ == '__main__':
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
            exit(0)
        elif opt in ("-d", "--debug"):
            logginglevel = logging.DEBUG
        elif opt in ("-k", "--key"):
            config.apikey = arg

    log_format = "[%(levelname)s] %(message)s"
    if logginglevel == logging.DEBUG:
        log_format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s"

    logging.basicConfig(
        level=logginglevel,
        format=log_format,
        handlers=[logging.StreamHandler(),
                  logging.FileHandler('debug.log', mode='w')])

    logging.debug(f"Luxor API key: {config.apikey}")

    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open
    # Also, this script won't exit when you close the webpage otherwise - probably something to do with the thread running session.hold()
    start_server(main, port=8080, debug=True)


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
