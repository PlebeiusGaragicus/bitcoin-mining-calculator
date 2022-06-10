import threading

from pywebio import pin
from pywebio import output

from constants import *
from data import *


###################################### THIS FUNCTION ROCKS!!!!!!!!! SAVE THIS!!!!!!!
#def popup_input(pins, names, title):
# onchangepinname='examples', onchange=changeentries)
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
        This creates a pop-up that asks the user for the bitcoin price
        This is used if we were unable to download the price from the internet
    """
    result = popup_input([
        pin.put_input('price', label='bitcoin price', type='float', value=pin.pin[PIN_BTC_PRICE_NOW])
        ], names=['price'], title="What is the current bitcoin price?")

    # USER HIT CANCEL
    if result == None:
        return -1

    if result['price'] == None or result['price'] <= 0:
        output.toast("invalid price")
        return -1
    else:
        p = result['price']

    return p


#####################################
def popup_get_stats_from_user() -> bool:
    """
        this pop up asks the user for network stats
    """
    result = popup_input([
        pin.put_input('in_height', label='block height', type='number', value=pin.pin[PIN_HEIGHT]),
        #pin.put_input('difficulty', label='difficulty', type='number', value=ns.difficulty),
        pin.put_input('in_hashrate', label='network hashrate (in terahashes)', type='float', value=pin.pin[PIN_NETWORKHASHRATE]),
        pin.put_input('in_price', label='bitcoin price', type='float', value=pin.pin[PIN_BTC_PRICE_NOW]),
        pin.put_input('in_fee', label='average fee (in satoshi)', type='float', value=pin.pin[PIN_AVERAGEFEE])
        ], names=['in_height', 'in_hashrate', 'in_price', 'in_fee'], title="Enter the current bitcoin network status")

    # USER HIT CANCEL
    if result == None:
        return False

    # VERIFY USER INPUT
    if result['in_height'] == None or result['in_height'] < 0:
        output.toast("invalid height")
        return False
    else:
        h = result['in_height']
        # d = result['difficulty']
    if result['in_hashrate'] == None or result['in_hashrate'] <= 0:
        output.toast("invalid hashrate")
        return False
    else:
        nh = result['in_hashrate']
    if result['in_price'] == None or result['in_price'] <= 0:
        output.toast("invalid price")
        return False
    else:
        p = result['in_price']
    if result['in_fee'] == None or result['in_fee'] <= 0:
        output.toast("invalid fee")
        return False
    else:
        f = result['in_fee']

    # TODO clean these numbers up...?  Round them???
    pin.pin[PIN_BTC_PRICE_NOW] = p
    pin.pin[PIN_BOUGHTATPRICE] = p
    pin.pin[PIN_HEIGHT] = h
    pin.pin[PIN_AVERAGEFEE] = f
    pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
    pin.pin[PIN_NETWORKHASHRATE] = nh

    return True








##############################
def popup_currencyconverter():
    def updateprice():
        pin.pin['convertprice'] = get_price() # query_bitcoinprice()

    def convert_to_sat():
        try:
            amnt = float(pin.pin["amount"])
            price = float(pin.pin["convertprice"])
            if amnt < 0 or price < 0:
                return
        except Exception as e:
            logging.exception()
            return
        r = float(ONE_HUNDRED_MILLION * (amnt / price))
        pin.pin["result"] = f"${amnt:,.2f} @ ${price:,.2f} = {r:.2f} sats / {r / ONE_HUNDRED_MILLION:.2f} bitcoin\n" + pin.pin['result']

    def convert_to_usd():
        try:
            amnt = float(pin.pin["amount"])
            price = float(pin.pin["convertprice"])
            if amnt < 0 or price < 0:
                return
        except Exception as e:
            logging.exception()
            return
        r = amnt * (price / ONE_HUNDRED_MILLION)
        pin.pin["result"] = f"{amnt:,.2f} sats @ ${price:,.2f} = ${r:,.2f}\n" + pin.pin['result']

    output.popup('USD - BTC converter', content=[
        output.put_row(content=[
            output.put_column(content=[
                pin.put_input("convertprice", type="float", label="Price of bitcoin:", value=get_price()),
                output.put_button("refresh price", onclick=updateprice)
                ]),
            output.put_column(content=[
                pin.put_input("amount", type="float", label="Amount to convert"),
                output.put_column(content=[
                    output.put_button("sats -> dollars", onclick=convert_to_usd),
                    output.put_button("dollars -> sats", onclick=convert_to_sat)
                    ])
                ])
        ]),
        pin.put_textarea("result", label="Result:", value="", readonly=True)
    ], closable=True)


def showstepbystep():
    # use 1TH and show calculation for hash value.. ETC ETC ETC
    output.toast("not implemented yet... sorry")

def feeanalysis():
    output.toast("not implemented yet... sorry")

def hashratehistory():
    # https://www.tradingview.com/
    output.toast("not implemented yet... sorry")

def pricehistory():
    # make a fucking moving average
    output.toast("not implemented yet... sorry")
