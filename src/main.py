# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
"""
This is the main module that you run
"""

import sys
import getopt
import threading
import logging

import pywebio

from constants import *
import config
import webio

def cleanup():
    logging.info("The web page was closed - goodbye")
    exit(0)


def main():
    pywebio.session.set_env(title="bitcoin mining profit calculator")

    t = threading.Thread(group=None, target=pywebio.session.hold)
    pywebio.session.register_thread( t )
    t.start()
    pywebio.session.defer_call(cleanup)

    webio.show_user_interface_elements()
    webio.refresh()

#############################
if __name__ == '__main__':
    logginglevel = logging.INFO
    try:
      opts, args = getopt.getopt(args=sys.argv[1:], shortopts="hdk:", longopts=['help', 'debug', 'key=', 'rpcip=', 'rpcuser='])
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
        elif opt == '--rpcip':
            config.RPC_ip_port = arg
        elif opt == '--rpcuser':
            config.RPC_user_pass = arg

    log_format = "[%(levelname)s] %(message)s"
    if logginglevel == logging.DEBUG:
        log_format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s"

    logging.basicConfig(
        level=logginglevel,
        format=log_format,
        handlers=[logging.StreamHandler(),
                  logging.FileHandler('debug.log', mode='w')])

    if not None in (config.RPC_ip_port, config.RPC_user_pass):
        config.RPC_enabled = True
        logging.info(f"using supplied RPC ip/port of {config.RPC_ip_port}")
        logging.info(f"using supplied RPC user/pass of {config.RPC_user_pass}")
    else:
        logging.error("You need to use both --rpcip and --rpcuser when calling script to enable RPC - QUITTING")
        exit(1)

    if config.apikey != None:
        logging.info(f"Luxor API key: {config.apikey}")

    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open
    # Also, this script won't exit when you close the webpage otherwise - probably something to do with the thread running session.hold()
    pywebio.start_server(main, port=8080, debug=True)
