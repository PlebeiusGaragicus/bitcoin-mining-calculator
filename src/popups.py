# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This module contains the functions for all the cool popups ;)
"""

import threading
import logging

from pywebio import pin
from pywebio import output

import plotly.graph_objects as go
from plotly.subplots import make_subplots
#from plotly.graph_objects import make_subplots
import pandas as pd

import config
from constants import *
import calcs
import data
import node
import luxor
import webio

#########################################################################
# shamelessly stolen from here and modified
# https://pywebio.readthedocs.io/en/latest/_modules/pywebio_battery/interaction.html#popup_input
def popup_input(pins, names, title, onchangepinname=None, callback=None):
    """
        Show a form in popup window.
        :param list pins: pin output list.
        :param list pins: pin name list.
        :param str title: model title.
        :return: return the form as dict, return None when user cancel the form.
    """
    if not isinstance(pins, list):
        pins = [pins]

    event = threading.Event()
    confirmed_form = None

    def onclick(val):
        nonlocal confirmed_form
        confirmed_form = val
        event.set()

    pins.append(output.put_buttons([
        {'label': 'Submit', 'value': True},
        {'label': 'Cancel', 'value': False, 'color': 'danger'},
    ], onclick=onclick))
    output.popup(title=title, content=pins, closable=False)
    
    if not onchangepinname == None:
        pin.pin_on_change(onchangepinname, onchange=callback)

    event.wait()
    output.close_popup()
    if not confirmed_form:
        return None

    return {name: pin.pin[name] for name in names}

#################################
def popup_get_price_from_user():
    """
        This creates a popup that asks the user for the bitcoin price
        This is used if we can't download the price from the internet
    """
    result = popup_input([
        pin.put_input('user_price', label='bitcoin price', type='float', value=pin.pin[PIN_BTC_PRICE_NOW])
        ], names=['user_price'], title="What is the current bitcoin price?")

    # USER HIT CANCEL
    if result == None:
        return -1

    if result['user_price'] == None or result['user_price'] <= 0:
        output.toast("invalid price")
        return -1
    else:
        p = result['user_price']

    return p

#####################################
def popup_get_stats_from_user() -> bool:
    """
        This pop up asks the user for network stats - used when we can't get data from a node or the internet
    """
    result = popup_input([
        pin.put_input('in_height', label='block height', type='number'),
        pin.put_input('in_diff', label='difficulty', type='number')
        #pin.put_input('in_hashrate', label='network hashrate (in terahashes)', type='float', value=pin.pin[PIN_NETWORKHASHRATE]),
        #pin.put_input('in_price', label='bitcoin price', type='float', value=pin.pin[PIN_BTC_PRICE_NOW]),
        #pin.put_input('in_fee', label='average fee (in satoshi)', type='float', value=pin.pin[PIN_AVERAGEFEE])
        ], names=['in_height', 'in_diff'], title="Enter the current bitcoin network status")

    # USER HIT CANCEL
    if result == None:
        return False

    # VERIFY USER INPUT
    if result['in_height'] == None or result['in_height'] < 0:
        output.toast("invalid height")
        return False
    else:
        h = result['in_height']
    
    if result['in_diff'] == None or result['in_diff'] < 0:
        output.toast("invalid difficulty")
        return False
    else:
        d = result['in_diff']

    # if result['in_hashrate'] == None or result['in_hashrate'] <= 0:
    #     output.toast("invalid hashrate")
    #     return False
    # else:
    #     nh = result['in_hashrate']

    # if result['in_price'] == None or result['in_price'] <= 0:
    #     output.toast("invalid price")
    #     return False
    # else:
    #     p = result['in_price']

    # if result['in_fee'] == None or result['in_fee'] <= 0:
    #     output.toast("invalid fee")
    #     return False
    # else:
    #     f = result['in_fee']

    # TODO clean these numbers up...?  Round them???
    #pin.pin[PIN_BTC_PRICE_NOW] = p
    #pin.pin[PIN_BOUGHTATPRICE] = p
    pin.pin[PIN_HEIGHT] = h
    pin.pin[PIN_NETWORKDIFFICULTY] = d
    #pin.pin[PIN_AVERAGEFEE] = f
    #pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
    #pin.pin[PIN_NETWORKHASHRATE] = nh

    return True

##############################
def popup_currencyconverter():
    """
        This popup allows you to convert from fiat to bitcoin and back
    """
    def updateprice():
        pin.pin['convertprice'] = data.get_price() # query_bitcoinprice()

    def convert_to_sat():
        try:
            amnt = float(pin.pin["amount"])
            price = float(pin.pin["convertprice"])
            if amnt < 0 or price < 0:
                return
        except Exception:
            logging.debug("", exc_info=True)
            return
        r = float(ONE_HUNDRED_MILLION * (amnt / price))
        pin.pin["result"] = f"${amnt:,.2f} @ ${price:,.2f} = {r:,.2f} sats / {r / ONE_HUNDRED_MILLION:.2f} bitcoin\n" + pin.pin['result']

    def convert_to_fiat():
        try:
            amnt = float(pin.pin["amount"])
            price = float(pin.pin["convertprice"])
            if amnt < 0 or price < 0:
                return
        except Exception as e:
            logging.debug("", exc_info=True)
            return
        r = amnt * (price / ONE_HUNDRED_MILLION)
        pin.pin["result"] = f"{amnt:,.2f} sats @ ${price:,.2f} = ${r:,.2f}\n" + pin.pin['result']

    output.popup('USD - BTC converter', content=[
        output.put_row(content=[
            output.put_column(content=[
                pin.put_input("convertprice", type="float", label="Price of bitcoin:", value=config.price),
                output.put_button("refresh price", onclick=updateprice)
                ]),
            output.put_column(content=[
                pin.put_input("amount", type="float", label="Amount to convert"),
                output.put_column(content=[
                    output.put_button("sats -> fiat", onclick=convert_to_fiat),
                    output.put_button("fiat -> sats", onclick=convert_to_sat)
                    ])
                ])
        ]),
        pin.put_textarea("result", label="Result:", value="", readonly=True)
    ], closable=True)

##########################
def popup_fee_analysis():
    """
        This creates a popup that averages the last 144 blocks in order to average transaction fees

        TODO check if we are using a pruned node and warn the user
    """

    if config.node_path != None:
        f = node.average_block_fee(config.node_path)
    else:
        f = data.get_average_block_fee_from_internet()

    pin.pin[PIN_AVERAGEFEE] = f
    pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
    webio.update_numbers()

###########################
def popup_price_history():
    """
        This is the popup that shows the price history of bitcoin
    """

    price_df = data.get_luxor_price_as_df()

    if price_df == None:
        output.toast("Error getting price data from Luxor", color='error')

    logging.debug(price_df)

    fig = go.Figure(data=go.Ohlc(x=price_df['timestamp'],
                        open=price_df['open'],
                        high=price_df['high'],
                        low=price_df['low'],
                        close=price_df['close']))

    pr = fig.to_html(include_plotlyjs="require", full_html=False)

    output.popup('bitcoin price history', size=output.PopupSize.LARGE, content=[
        output.put_html(pr)
        ], closable=True)

#################################
def popup_difficulty_history():
    """
        Return a list of network difficulty at first block of each epoch (0, 2016, ...)
        Return None on error
    """
    if config.apikey == None:
        output.toast("Luxor API key is not supplied", color='error')
        return

    lux = luxor.LuxorAPI(host=luxor.LUXOR_ENDPOINT, method='POST', key=config.apikey)

    dhx = lux.get_network_difficulty("_1_YEAR")['data']['getChartBySlug']['data']
    nh = lux.get_network_hashrate("_1_YEAR")['data']['getNetworkHashrate']['nodes']
    # Note - See issue: https://github.com/LuxorLabs/hashrateindex-api-python-client/issues/4

    #fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig = make_subplots()

    fig.add_trace(
        go.Scatter(
            x=[*range(len(dhx) // 2)],
            y=[i['difficulty'] for x, i in enumerate(dhx) if x % 2 == 0],
            name="difficulty",
            line_color="#A50CAC" # PURPLE
        ), secondary_y=False)
    fig.add_trace(
        go.Scatter(
            x=[*range(len(nh))],
            y=[i['networkHashrate'] for i in nh],
            name="hashrate",
            line_color="#5A5AAA"
        ), secondary_y=True)

    pr = fig.to_html(include_plotlyjs="require", full_html=False)

    output.popup('network difficulty history', size=output.PopupSize.LARGE, content=[
            output.put_html(pr)
        ], closable=True)


#################################
def popup_breakeven_analysis():
    """
        This creates a popup with a break-even analysis tool for price, price/kWh and network hashrate
    """
    def update_break_even( callback_throwaway ):
        """
            This call back is used for every onchange= 'pin' input field.
            We just continuously update the numbers on every keyboard stroke
        """
        try:
            wattage = int(pin.pin['be_wattage'])
            hashrate = float(pin.pin['be_hashrate'])
            poolfee = float(pin.pin['be_poolfee']) / 100

            height = int(pin.pin['be_height'])
            blocktxfee = float(pin.pin['be_blocktxfee'])

            rate = float(pin.pin['be_rate'])
            nh = float(pin.pin['be_nh']) * MEGAHASH # convert EH/s to TH/s
            price = float(pin.pin['be_price'])
        except Exception as e:
            print("Exception:", e)
            return

        if rate == 0:
            print("cost / kWh is 0 ...")
            return

        price_satoshi = price / ONE_HUNDRED_MILLION

        try:
            reward = calcs.block_subsity(height) + blocktxfee
            be_nh = (reward * hashrate * (1 - poolfee) * price_satoshi * 6000) / (rate * wattage)
            be_nh /= MEGAHASH # turn TH/s -> EH/s
            be_p = ONE_HUNDRED_MILLION * ((nh * rate * wattage) / (reward * hashrate * (1 - poolfee) * 6000))
            be_rate = (reward * hashrate * (1 - poolfee) * price_satoshi * 6000) / (nh * wattage)
        except ZeroDivisionError as e:
            logging.exception('')
            be_nh = be_p = be_rate = 0

        pin.pin_update('res_rate', value=f"{be_rate:.3f}")
        pin.pin_update('res_nh', value=f"{be_nh:,.2f}")
        pin.pin_update('res_price', value=f"{be_p:,.2f}")

    #########################
    # THIS IS A CALLBACK FOR THE BELOW
    #########################
    def height_waschanged(h):
        pin.pin['be_subsidy'] = f"{calcs.block_subsity(h):,}"
        update_break_even(None)

    try:
        #nh = int(ur.urlopen(ur.Request('https://blockchain.info/q/hashrate')).read()) / 1000
        #height = int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read())
        #price =  int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))
        #nh = pin.pin[PIN_NETWORKHASHRATE]
        nh = f"{data.get_hashrate_from_difficulty( pin.pin[PIN_NETWORKDIFFICULTY]/MEGAHASH ):.2f}"
        height = pin.pin[PIN_HEIGHT]
        price = pin.pin[PIN_BTC_PRICE_NOW]
    except Exception as e:
        logging.exception('')
        output.toast("Unable to get bitcoin network stats", duration=5)
        nh = height = price = 0

    try:
        with output.popup("Break-even analysis", size=output.PopupSize.LARGE):
            output.put_table(tdata=[[
                pin.put_input(name='be_wattage', type='number', label="Wattage", value=pin.pin[PIN_WATTAGE]),
                pin.put_input(name='be_hashrate', type='float', label="Hashrate (terahash)", value=pin.pin[PIN_HASHRATE]),
                pin.put_input(name='be_poolfee', type='float', label="Pool fee %", value=pin.pin[PIN_POOLFEE])
            ]])
            pin.pin_on_change('be_wattage', onchange=update_break_even)
            pin.pin_on_change('be_hashrate', onchange=update_break_even)
            pin.pin_on_change('be_poolfee', onchange=update_break_even)

            output.put_table(tdata=[[
                pin.put_input(name='be_height', type='float', label="block height", value=height),
                pin.put_input(name='be_subsidy', type='text', label="current block subsidy", value=f"{calcs.block_subsity(height):,}", readonly=True),
                pin.put_input(name='be_blocktxfee', type='float', label="Average block fees", value=pin.pin[PIN_AVERAGEFEE])
            ]])
            pin.pin_on_change('be_height', onchange=height_waschanged)
            pin.pin_on_change('be_subsidy', onchange=update_break_even)
            pin.pin_on_change('be_blocktxfee', onchange=update_break_even)

            output.put_table(tdata=[[
                pin.put_input(name='be_rate', type='float', label="Cost / kWh", value=pin.pin[PIN_KWH_RATE]),
                pin.put_input(name='be_nh', type='float', label="Network hashrate (exahash)", value=nh),
                pin.put_input(name='be_price', type='float', label="Bitcoin price", value=price)
            ]])
            pin.pin_on_change('be_rate', onchange=update_break_even)
            pin.pin_on_change('be_nh', onchange=update_break_even)
            pin.pin_on_change('be_price', onchange=update_break_even)

            output.put_markdown("---")
            output.put_text("Break even:")
            output.put_table(tdata=[[
                pin.put_input(name='res_rate', type='text', label="Cost / kWh", readonly=True),
                pin.put_input(name='res_nh', type='text', label="Network hashrate (exahash)", readonly=True),
                pin.put_input(name='res_price', type='text', label="Bitcoin price", readonly=True)
            ]])

            # then we run this 'callback' so the popup will auto-calculate
            update_break_even( None )
    except Exception as e:
        logging.exception('')
