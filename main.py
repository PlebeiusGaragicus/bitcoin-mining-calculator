# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This is the main module that you run
"""

import threading
import logging

import pywebio
from pywebio import pin
from pywebio import output
from pywebio import session

from constants import *
from nodes import *
from popups import *
from data import *
from webio import *
from calcs import *

def init():
    """
        This tries to get the latest bitcoin network data + price
    """
    # make init a popup??? but you can't have a popup call a popup..... maybe the popup will appear when data is being downloaded!!!

    path = useful_node()

    if path != None:
        h = node_blockheight(path)

        f = node_avgblockfee(path)
        #f = node_avgblockfee_popup(path, nBlocks)
        nh = node_networkhashps(path)

        p = get_price() # query_bitcoinprice()

        if p == -1:
            #output.toast("Unable to download current bitcoin price from <some website>")
            logging.error("Unable to get current bitcoin price")
            p = popup_get_price_from_user()

            # TODO check p is no -1; loop endlessly?
            logging.info(f"Using user-supplied Bitcoin price: ${p:,.2f}")
        else:
            logging.info(f"Bitcoin price: ${p:,.2f}")

        pin.pin[PIN_BTC_PRICE_NOW] = p
        pin.pin[PIN_BOUGHTATPRICE] = p
        pin.pin[PIN_HEIGHT] = h
        pin.pin[PIN_AVERAGEFEE] = f
        pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
        pin.pin[PIN_NETWORKHASHRATE] = nh

    else:
        # if we're not able to get stats from the internet:
        if not get_stats_from_luxor():
            if not get_stats_from_internet():

                # run an endless loop until user provides valid network data
                r = popup_get_stats_from_user()
                while r == False:
                    r = popup_get_stats_from_user()

###############################
def main():
    session.set_env(title="bitcoin mining profit calculator")

    # https://pywebio.readthedocs.io/en/latest/platform.html
    # https://pywebio.readthedocs.io/en/v1.2.2/guide.html#server-mode-and-script-mode
    # https://github.com/pywebio/PyWebIO/blob/dev/demos/bokeh_app.py
    # I can't believe this fucking works!!!!  Will it ever cause problems? #shrug
    t = threading.Thread(target=session.hold)
    session.register_thread( t )
    t.start()

    with output.use_scope('main', clear=True):
        output.put_markdown( MAIN_TEXT )
        output.put_button("USD - BTC converter", onclick=popup_currencyconverter, color='info')

    show_settings()
    init()

#############################
if __name__ == '__main__':
    #logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler('debug.log', mode='w')])

    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open, you have to click the link
    pywebio.start_server(main, port=8080, debug=True)
    #main()
