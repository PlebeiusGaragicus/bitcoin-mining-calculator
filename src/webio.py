# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This module contains the callbacks to the pywebio fields and
a lot of the code that runs the pywebio user interface
"""

from __future__ import print_function
import datetime
import logging

from pywebio import pin
from pywebio import output

import config
from constants import *
import data
import node
import calcs
import popups

##################################
def enter_debug_values() -> None:
    pin.pin[PIN_WATTAGE] = 3050
    pin.pin[PIN_COST] = 5375
    pin.pin[PIN_HASHRATE] = 90
    pin.pin[PIN_BOUGHTATPRICE] = 29500

################
def refresh() -> None:
    """
        This function is called (1) at startup and (2) when the "refresh data" button is pushed
    """
    output.toast("refreshing network data...", color='info')
    data.download_bitcoin_network_data()
    #pin.pin[PIN_BTC_PRICE_NOW] = config.price
    #pin.pin[PIN_HEIGHT] = config.height
    #pin.pin[PIN_NETWORKDIFFICULTY] = config.difficulty
    enter_debug_values()
    update_timestamp()
    update_numbers() # this is the callback function used to ensure all UI read_only fields are updated
    output.toast("refresh done", color='success')

###############################
def make_projection() -> None:
    """
        THIS FUNCTION TAKES THE VALUES FROM THE INPUT FIELDS AND RUNS THE PROJECTION...
    """
    output.toast("calculating...", color='warn', duration=1)
    logging.info("running show_projection()")

    months = get_entered_months()
    height = get_entered_height()
    avgfee = get_entered_fees()
    hashrate = get_entered_hashrate()
    wattage = get_entered_wattage()
    price = get_entered_price()
     # TODO figure out my strategy for this thang!!
    price_when_bought = get_entered_bought_price()

    pricegrow = float(pin.pin[PIN_PRICEGROW] / 100)
    pricegrow2 = float(pin.pin[PIN_PRICEGROW2] / 100)
    pricelag = int(pin.pin[PIN_LAG])
    
    diff = get_entered_difficulty()
    hashgrow = float(pin.pin[PIN_HASHGROW] / 100)

    kWh_rate = get_entered_rate()
    opex = get_entered_opex()
    capex = get_entered_machine_cost()
    resell = get_entered_resell_percent()
    poolfee = get_entered_poolfee()

    if None in (months, height, avgfee, hashrate, wattage, price,
                pricegrow, pricegrow2, pricelag, diff,
                hashgrow, kWh_rate, opex, capex, resell, poolfee):
        output.toast("Error - an input field was left blank (or is invalid)")
        logging.error("None variable passed to calculate_projection()")
        return

    with output.use_scope('projection', clear=True):
        output.put_markdown( "# PROJECTION SUMMARIES:" )

    res = calcs.calculate_projection(
        months = months,
        height = height,
        avgfee = avgfee,
        hashrate = hashrate,
        wattage = wattage,
        price = price,
        pricegrow = pricegrow,
        pricegrow2 = pricegrow2,
        pricelag = pricelag,
        network_difficulty = diff,
        hashgrow = hashgrow,
        kWh_rate = kWh_rate,
        opex = opex,
        capex_in_sats = calcs.btc(capex, bitcoin_price=price_when_bought),
        resale = resell,
        poolfee = poolfee,
    )

    config.analysis_number += 1

    table = calcs.make_table_string(res)
    with output.use_scope("result"):
        output.put_collapse(title=f"analysis #{config.analysis_number}", content=[
            output.put_html( calcs.pretty_graph(res) ),
            output.put_collapse("Monthly Breakdown Table", content=[
            output.put_markdown( table ),
            output.put_table(tdata=[[
                    output.put_file('projection.csv', content=b'123,456,789'),
                    output.put_text("<<-- Download results as CSV file")
                ]])
        ])
        ], position=output.OutputPosition.TOP, open=True)

    output.toast("done.", color='success', duration=1)

#######################
def show_projection() -> None:
    """
        This takes all the entered variables, runs an earnings projection and displays the results
    """
    output.toast("calculating...", color='warn', duration=1)
    logging.info("running show_projection()")

    months = get_entered_months()
    height = get_entered_height()
    avgfee = get_entered_fees()
    hashrate = get_entered_hashrate()
    wattage = get_entered_wattage()
    price = get_entered_price()
     # TODO figure out my strategy for this thang!!
    price_when_bought = get_entered_bought_price()

    pricegrow = float(pin.pin[PIN_PRICEGROW] / 100)
    pricegrow2 = float(pin.pin[PIN_PRICEGROW2] / 100)
    pricelag = int(pin.pin[PIN_LAG])
    
    diff = get_entered_difficulty()
    hashgrow = float(pin.pin[PIN_HASHGROW] / 100)

    kWh_rate = get_entered_rate()
    opex = get_entered_opex()
    capex = get_entered_machine_cost()
    resell = get_entered_resell_percent()
    poolfee = get_entered_poolfee()

    if None in (months, height, avgfee, hashrate, wattage, price,
                pricegrow, pricegrow2, pricelag, diff,
                hashgrow, kWh_rate, opex, capex, resell, poolfee):
        output.toast("Error - an input field was left blank (or is invalid)")
        logging.error("None variable passed to calculate_projection()")
        return

    with output.use_scope('projection', clear=True):
        output.put_markdown( "# PROJECTION SUMMARIES:" )


    res = calcs.calculate_projection(
        months = months,
        height = height,
        avgfee = avgfee,
        hashrate = hashrate,
        wattage = wattage,
        price = price,
        pricegrow = pricegrow,
        pricegrow2 = pricegrow2,
        pricelag = pricelag,
        network_difficulty = diff,
        hashgrow = hashgrow,
        kWh_rate = kWh_rate,
        opex = opex,
        capex_in_sats = calcs.btc(capex, bitcoin_price=price_when_bought),
        resale = resell,
        poolfee = poolfee,
    )

    config.analysis_number += 1

    table = calcs.make_table_string(res)
    with output.use_scope("result"):
        output.put_collapse(title=f"analysis #{config.analysis_number}", content=[
            output.put_html( calcs.pretty_graph(res) ),
            output.put_collapse("Monthly Breakdown Table", content=[
            output.put_markdown( table ),
            output.put_table(tdata=[[
                    output.put_file('projection.csv', content=b'123,456,789'),
                    output.put_text("<<-- Download results as CSV file")
                ]])
        ])
        ], position=output.OutputPosition.TOP, open=True)

    output.toast("done.", color='success', duration=1)

#######################
def show_user_interface_elements():

    output.put_markdown( MAIN_TEXT )
    output.put_collapse(title="TOOLS:", content=[
        output.put_button("fiat <-> bitcoin converter", onclick=popups.popup_currencyconverter, color='info'),
        output.put_button("refresh data", onclick=refresh),
        output.put_button("break-even analysis", onclick=popups.popup_breakeven_analysis, color='info'),
        output.put_button("block fee analysis", onclick=popups.popup_fee_analysis),
        output.put_button("price history analysis", onclick=popups.popup_price_history),
        output.put_button("hashrate history analysis", onclick=popups.popup_difficulty_history)
    ])

    ### NETWORK STATE ### NETWORK STATE ### NETWORK STATE ### NETWORK STATE ### NETWORK STATE
    output.put_markdown("### Bitcoin network state")
    output.put_table([[
        pin.put_input(name=PIN_BTC_PRICE_NOW, type='float', label="Bitcoin price $", value=0),
        pin.put_input(name=PIN_HEIGHT, type='float', label="blockchain height", value=0),
        pin.put_input(name=PIN_AVERAGEFEE, type='float', label="average tx fee", value=0),
        pin.put_input(name=PIN_SUBSIDY, type='text', label="total reward", value=0, readonly=True)
    ],[
        pin.put_input(name=PIN_NETWORKDIFFICULTY, type='float', label="network difficulty", value=0),
        pin.put_input(name=PIN_NETWORKHASHRATE, type='text', label="network TH/s", value=0, readonly=True),
        pin.put_input(name=PIN_HASHVALUE, type='text', label="hash value", value=0, readonly=True, help_text='satoshi earned per Terahash per day'),
        pin.put_input(name=PIN_HASHPRICE, type='text', label="hash price", value=0, readonly=True, help_text='hash value denominated in fiat at today\'s price')
        ]])
    pin.pin_on_change(name=PIN_BTC_PRICE_NOW, onchange=update_numbers)
    pin.pin_on_change(name=PIN_HEIGHT, onchange=update_height)
    pin.pin_on_change(name=PIN_AVERAGEFEE, onchange=update_numbers)
    pin.pin_on_change(name=PIN_NETWORKDIFFICULTY, onchange=update_numbers)
    
    ### MINER SPECIFICATION ### MINER SPECIFICATION ### MINER SPECIFICATION ### MINER SPECIFICATION ### MINER SPECIFICATION 
    output.put_markdown('### hardware specification / capital expenditure')
    output.put_table([[
            pin.put_input(name=PIN_BOUGHTATPRICE, type='float', label='bitcoin price at time of purchase', value=pin.pin[PIN_BTC_PRICE_NOW]),
            pin.put_input(name=PIN_COST, type='float', label='Fiat cost of machine'),
            pin.put_input(name=PIN_SAT_PER_TH, type='text', label="satoshi / TH", readonly=True),
            pin.put_input(name=PIN_FIAT_PER_TH, type='text', label="$ / TH", readonly=True)
        #],[
        #    pin.put_input(name='wattdollar', label="WattDollar", readonly=True, value='', help_text="The product of an ASIC’s watts/Th multiplied by $/Th")
        ]])
    pin.pin_on_change(name=PIN_BOUGHTATPRICE, onchange=update_numbers)
    pin.pin_on_change(name=PIN_COST, onchange=update_numbers)
    output.put_table([[
            pin.put_input(name=PIN_WATTAGE, type='float', label="Wattage"),
            pin.put_input(name=PIN_HASHRATE, type='float', label='Hashrate (in terahash)'),
            pin.put_input(name=PIN_EFF, type='float', label="hashing efficiency (W/TH)", readonly=True)
    ]])
    pin.pin_on_change(name=PIN_WATTAGE, onchange=update_numbers)
    pin.pin_on_change(name=PIN_HASHRATE, onchange=update_numbers)

    output.put_markdown("### hardware resale / depreciation recapture")
    output.put_table([[
            pin.put_checkbox(name=PIN_NEVERSELL, options=[OPTION_NEVERSELL], value=False),
            pin.put_input(name=PIN_MONTHSTOPROJECT, type='number', value=DEFAULT_MONTHSTOPROJECT, label='Months until you re-sell this miner', help_text="Months to run projection"),
            pin.put_input(name=PIN_RESELL, type='number', label="Resale %", help_text="% percent of purchase price", value=DEFAULT_RESELL),
            pin.put_input(name=PIN_RESELL_READONLY, type='text', label="Resale price", readonly=True)
    ]])
    pin.pin_on_change(name=PIN_NEVERSELL, onchange=toggle_resell) # this toggles (disable/enables) other input fields
    pin.pin_on_change(PIN_RESELL, onchange=update_numbers)

    output.put_markdown("### Cost-of-production")
    output.put_table([[
        pin.put_input(PIN_KWH_RATE, type='float', label='cost per kilowatt-hour: $', value=DEFAUL_KPKWH),
        pin.put_input(PIN_POOLFEE, type='float', label='mining pool fee: %', value= DEFAULT_POOL_FEE),
        pin.put_input(PIN_HASHEXPENSE, type='text', label='hash expense', value=0, readonly = True, help_text='your cost-of-production per Terahash per day'),
        pin.put_input(PIN_OPEX, type='float', label='monthly operational cost: $', value= DEFAULT_OPEX)
    ]])
    pin.pin_on_change(PIN_KWH_RATE, onchange=update_numbers)
    pin.pin_on_change(PIN_POOLFEE, onchange=update_numbers)
    pin.pin_on_change(PIN_OPEX, onchange=update_numbers)

    output.put_markdown("### Projection Parameters")

    output.put_table([[
        pin.put_input(name=PIN_PRICEGROW, type='float', value=DEFAULT_PRICEGROW, label='Monthly price growth: %', help_text='how fast do you predict the bitcoin price will grow month-to-month?'),
        #pin.put_slider(PIN_PRICEGROW_SLIDER, label='Price growth slider', value=DEFAULT_PRICEGROW,min_value=-10.0, max_value=20.0, step=0.1),
        pin.put_input(name=PIN_PRICEGROW2, type='float', value=DEFAULT_PRICEGROW2, label='Post-halvening price growth: %', help_text="How fast do you think the price will grow monthly post-halvening (and post 'lag')"),
        #pin.put_slider(name="post_halvening_slider", label='Price growth slider', value=DEFAULT_PRICEGROW2,min_value=-10.0, max_value=20.0, step=0.1),
        pin.put_input(name=PIN_LAG, type='float', value=DEFAULT_LAG, label='Halvening price lag (months)', help_text="The price growth post-halvening sometimes lags a few months..."),
        pin.put_input(name=PIN_HASHGROW, type='float', value=DEFAULT_HASHGROW, label='Monthly hashrate growth: %'),
        #pin.put_slider(PIN_HASHGROW_SLIDER, value=DEFAULT_HASHGROW,min_value=-2.0, max_value=10.0, step=0.1),
    ]])
    #pin.pin_on_change(PIN_PRICEGROW_SLIDER, onchange=pricegrow_slider)
    #pin.pin_on_change(name=PIN_PRICEGROW2_SLIDER, onchange=pricegrow2_slider)
    #pin.pin_on_change(PIN_HASHGROW_SLIDER, onchange=hashgrow_slider)
    #pin.pin_on_change(name=PIN_HASHGROW, onchange=hashgrow_waschanged)

    output.put_button( 'What might happen?', onclick=show_projection, color='danger' )
    output.put_button( 'new button', onclick=make_projection, color='success' )


##################################
def get_entered_price() -> float:
    """
        This returns the entered machine wattage
        None is returned on error (eg. input is blank) or is less than zero
    """
    try:
        ret = float(pin.pin[PIN_BTC_PRICE_NOW])
    except TypeError:
        logging.debug('machine hashrate - input field blank', exc_info=True)
        return None

    if ret < 0:
        return None
    return ret

#################################
def get_entered_height() -> int:
    """
        This returns the entered machine wattage
        None is returned on error (eg. input is blank) or is less than zero
    """
    try:
        ret = int(pin.pin[PIN_HEIGHT])
    except TypeError:
        logging.debug('machine hashrate - input field blank', exc_info=True)
        return None

    if ret < 0:
        return None
    return ret

#######################
def get_entered_fees() -> int:
    """
        This returns the entered machine wattage
        None is returned on error (eg. input is blank) or is less than zero
    """
    try:
        ret = int(pin.pin[PIN_AVERAGEFEE])
    except TypeError:
        logging.debug('average tx fee - input field blank', exc_info=True)
        return None

    if ret < 0:
        return None
    return ret

#################################
def get_entered_months() -> int:
    """
        This returns the entered months to project
        None is returned on error (eg. input is blank) or if number is less than 1
    """
    try:
        ret =  int(pin.pin[PIN_MONTHSTOPROJECT])
    except TypeError:
        logging.debug('months to project - input field blank', exc_info=True)
        return None

    if ret < 1:
        return None
    return ret

def get_entered_wattage() -> float:
    """
        This returns the entered machine wattage
        None is returned on error (eg. input is blank)
    """
    try:
        ret =  float(pin.pin[PIN_WATTAGE])
    except TypeError:
        logging.debug('input field blank', exc_info=True)
        return None

    if ret < 1:
        return None
    return ret

#####################################
def get_entered_difficulty() -> int:
    """
        This returns the entered network difficulty
        None is returned on error (eg. input is blank)
        TODO what is minimum difficulty?
    """
    try:
        ret =  int(pin.pin[PIN_NETWORKDIFFICULTY])
    except TypeError:
        logging.debug('input field blank', exc_info=True)
        return None

    if ret < 1: #TODO WHAT IS MINIMUM DIFFICULTY?
        return None
    return ret

def get_entered_wattage() -> float:
    """
        This returns the entered machine wattage
        None is returned on error (eg. input is blank)
    """
    try:
        ret =  float(pin.pin[PIN_WATTAGE])
    except TypeError:
        logging.debug('input field blank', exc_info=True)
        return None

    if ret < 1:
        return None
    return ret

def get_entered_hashrate() -> float:
    """
        This returns the entered machine hashrate
        None is returned on error (eg. input is blank) or if entered hashrate is less than 1
    """
    try:
        ret = float(pin.pin[PIN_HASHRATE])
    except TypeError:
        logging.debug('machine hashrate - input field blank', exc_info=True)
        return None
    
    if ret < 1:
        return None
    return ret

def get_entered_bought_price() -> float:
    """
        This returns the entered cost of the ASIC
        None is returned on error (eg. input is blank)
    """
    try:
        ret = float(pin.pin[PIN_BOUGHTATPRICE])
    except TypeError:
        logging.debug('bought at price - input field blank', exc_info=True)
        return None

    if ret < 1:
        return None
    return ret

def get_entered_machine_cost() -> float:
    """
        This returns the entered cost of the ASIC
        None is returned on error (eg. input is blank)
    """
    try:
        ret =  float(pin.pin[PIN_COST])
    except TypeError:
        logging.debug('machine cost - input field blank', exc_info=True)
        return None

    if ret < 1:
        return None
    return ret

###########################################
def get_entered_resell_percent() -> float:
    """
        This returns the entered cost of the ASIC
        None is returned on error (eg. input is blank) or is less than zero
    """
    try:
        ret =  float(pin.pin[PIN_RESELL] / 100)
    except TypeError:
        logging.debug('resell percent - input field blank', exc_info=True)
        return None

    if ret < 0.000:
        return None
    return ret

#################################
def get_entered_rate() -> float:
    """
        This returns the entered cost of the ASIC
        None is returned on error (eg. input is blank) or is less than zero
    """
    try:
        ret =  float(pin.pin[PIN_KWH_RATE])
    except TypeError:
        logging.debug('kWh rate - input field blank', exc_info=True)
        return None

    if ret < 0.0:
        return None
    return ret


####################################
def get_entered_poolfee() -> float:
    """
        This returns the entered cost of the ASIC
        None is returned on error (eg. input is blank)
    """
    try:
        ret =  float(pin.pin[PIN_POOLFEE])
    except TypeError:
        logging.debug('mining pool fee - input field blank', exc_info=True)
        return None

    if ret < 0.00:
        return None

    return ret / 100 # becuaes it's a percent


#################################
def get_entered_opex() -> float:
    """
        This returns the entered cost of the ASIC
        None is returned on error (eg. input is blank)
    """
    try:
        ret =  float(pin.pin[PIN_OPEX])
    except TypeError:
        logging.debug('monthly operational cost - input field blank', exc_info=True)
        return None

    if ret < 0.00:
        return None
    return ret



############################
def update_price() -> None:
    """
        This is called when the user enters an 'old' block height and we run a historical projection

        This function essentially takes the entered height, queries coinbase for the price, and updates the PIN_PRICE field
    """
    # this feature is only available when running a node that is NOT pruned
    #if config.node_path == None or config.pruned:
    if config.node_path == None and config.RPC_enabled == False:
        return

    h = get_entered_height()
    if h == None:
        return

    if h < 365000:
        output.toast("price data does not exist for block before 365000")
        pin.pin_update(PIN_BTC_PRICE_NOW, value=0)
        return

    # a height in the future
    if h > config.height:
        return

    # on second thought... just say no to pruned nodes, kids.
    if config.pruned and h < config.pruned_height:
        logging.debug("This node is pruned and that block is not in memory...")
        return

    logging.debug(f"update_price {h=}")

    unix = node.get_block_unix_time(h)
    if unix == None: #pruned node.. or, we just don't have the data for that height
        return

    p = data.coinbase_fetch_price_history(unix, unix+86400)
    try:
        price = (p['open'][0] + p['close'][0]) / 2
        logging.debug(f"{price=}")
        price = round(price, 2)
    except IndexError:
        output.toast(f"unable to load the price for block height {h}")
        pin.pin_update(PIN_BTC_PRICE_NOW, value='')
        return
    
    logging.debug(f"we got a price of {price}")

    pin.pin_update(PIN_BTC_PRICE_NOW, value=price) #nah, just leave it...

################################
def update_timestamp() -> None:
    # this feature only works if you have a node
    if config.node_path == None and config.RPC_enabled == False:
        return

    h = get_entered_height()

    if h == None:
        pin.pin_update(PIN_HEIGHT, help_text='')
        return

    if h > config.height:
        return

    try:
        t = node.get_block_unix_time(h)
        t = datetime.datetime.fromtimestamp(t).isoformat(sep=' ', timespec='seconds')

    except Exception:
        #logging.exception('')
        logging.debug('', exc_info=True)
        output.toast("unable to get block time - are you running a pruned node?")
        pin.pin_update(PIN_HEIGHT, help_text='')
        return

    pin.pin_update(PIN_HEIGHT, help_text=t)

#################################
def update_difficulty() -> None:
    # this feature only works if you have a node
    if config.node_path == None and config.RPC_enabled == False:
        return

    h = get_entered_height()

    if h == None:
        return

    if h > config.height:
        return

    try:
        diff = node.getdifficulty(h)

        if diff == None:
            return
        
        pin.pin_update(PIN_NETWORKDIFFICULTY, value=diff)

    except Exception:
        #logging.exception('')
        logging.debug('', exc_info=True)
        output.toast("unable to get block difficulty - are you running a pruned node?")
        return

##############################
def update_subsity() -> None:
    height = get_entered_height()
    fees = get_entered_fees()

    if None in (height, fees):
        pin.pin[PIN_SUBSIDY] = ''
        pin.pin_update(PIN_SUBSIDY, help_text='')
        return

    total = calcs.block_subsity( height ) + fees
    pin.pin[PIN_SUBSIDY] = f"{total:,}"

    price = get_entered_price()

    if price == None:
        pin.pin_update(PIN_SUBSIDY, help_text='')
        return

    fiat_reward = calcs.fiat(total, price)
    pin.pin_update(PIN_SUBSIDY, help_text=f"$ {fiat_reward:,.2f}")

###############################
def update_hashrate() -> None:
    diff = get_entered_difficulty()

    if diff == None: # this is lame... I am lame for writing this... but this make the code consistant... and it works... so buzz off
        pin.pin[PIN_NETWORKHASHRATE] = ''
        pin.pin_update(PIN_NETWORKHASHRATE, help_text=f'')
        return

    nh = round(calcs.get_hashrate_from_difficulty(diff), 2)
    pin.pin[PIN_NETWORKHASHRATE] = f"{nh:,} TH/s"
    pin.pin_update(PIN_NETWORKHASHRATE, help_text=f"{nh/MEGAHASH:.2f} EH/s")

################################
def update_hashvalue() -> None:
    height = get_entered_height()
    fees = get_entered_fees()
    diff = get_entered_difficulty()

    if None in (height, fees, diff):
        pin.pin[PIN_HASHVALUE] = ''
        return

    try:
        nh = round(calcs.get_hashrate_from_difficulty(diff), 2)
        reward = calcs.block_subsity( height ) + fees
        r = reward / nh * EXPECTED_BLOCKS_PER_DAY
    except ZeroDivisionError:
        pin.pin[PIN_HASHVALUE] = ''
        return

    pin.pin[PIN_HASHVALUE] = f"{r:,.1f} sats"

################################
def update_hashprice() -> None:
    price = get_entered_price()

    try:
        # let's be lazy and just grab the hashvalue entry to use it
        s = str(pin.pin[PIN_HASHVALUE]).replace(',', '').replace(' sats', '')
        hv = float(s)
    except ValueError:
        pin.pin[PIN_HASHPRICE] = ''
        logging.debug('ummm...', exc_info=True)
        return
    
    if price == None:
        pin.pin[PIN_HASHPRICE] = ''
        return

    r = calcs.fiat(hv, price)
    pin.pin[PIN_HASHPRICE] = f"$ {r:,.4f}"

###########################
def update_cost() -> None:
    """
        ...
    """
    cost = get_entered_machine_cost()
    bought_price = get_entered_bought_price()

    if None in (cost, bought_price):
        pin.pin_update(name=PIN_COST, help_text='')
        return

    pin.pin_update(name=PIN_COST, help_text=f"{ONE_HUNDRED_MILLION * (cost/bought_price):,.1f} sats")

################################
def update_satsperth() -> None:
    """
        ...
    """
    hashrate = get_entered_hashrate()
    bought_price = get_entered_bought_price()
    cost = get_entered_machine_cost()

    if None in (hashrate, bought_price, cost):
        pin.pin[PIN_FIAT_PER_TH] = ''
        return

    ret = calcs.btc(cost, bought_price) / hashrate

    pin.pin[PIN_SAT_PER_TH] = f"{ret:,.2f}"

################################
def update_fiatperth() -> None:
    """
        ...
    """
    hashrate = get_entered_hashrate()
    cost = get_entered_machine_cost()

    if None in (hashrate, cost):
        pin.pin_update(PIN_FIAT_PER_TH, value='')
        return

    fiats_per_th = cost / hashrate

    # dollarsperth = cost / hashrate # uncaught DivideByZeroError
    #pin.pin[PIN_FIAT_PER_TH] = f"${dollarsperth:,.2f} / TH"
    pin.pin[PIN_FIAT_PER_TH] = f"{fiats_per_th:,.2f}"

##########################
def update_eff() -> None:
    """
        ...
    """
    wattage = get_entered_wattage()
    hashrate = get_entered_hashrate()

    if None in (wattage, hashrate):
        pin.pin[PIN_EFF] = None
        return

    try:
        eff = float(wattage / hashrate)
    except ZeroDivisionError:
        eff = None

    pin.pin[PIN_EFF] = f"{eff:,.2f}"

#############################
def update_resell() -> None:
    """
        ...
    """
    cost = get_entered_machine_cost()
    resell = get_entered_resell_percent()

    if None in (cost, resell):
        pin.pin_update(PIN_RESELL_READONLY, value='')
        print("cost", cost)
        print("resell", resell)
        return

    price = cost * resell

    pin.pin[PIN_RESELL_READONLY] = f"$ {price:,.2f}"

##########################
def toggle_resell( opt ) -> None:
    """
        This is the callback for the 'resell' radio button PIN_RESELL
    """
    if OPTION_NEVERSELL in opt:
        # NEVER SELL
        pin.pin_update(name=PIN_RESELL, readonly=True)
        pin.pin_update(name=PIN_MONTHSTOPROJECT, label="Months to run profit projection")
        pin.pin_update(name=PIN_MONTHSTOPROJECT, help_text="or, expected machine life span")
    else:
        # WILL SELL
        pin.pin_update(name=PIN_RESELL, readonly=False)
        pin.pin_update(name=PIN_MONTHSTOPROJECT, label="Months until you re-sell this miner")
        pin.pin_update(name=PIN_MONTHSTOPROJECT, help_text="")

##################################
def update_hashexpense() -> None:
    eff = pin.pin[PIN_EFF] # we're just going to read from this input field so we don't have to duplicate too much shit
    rate = get_entered_rate()
    poolfee = get_entered_poolfee()
    price = get_entered_price()

    try:
        hv = float(str(pin.pin[PIN_HASHVALUE]).replace(' sats', '').replace(',', ''))
    except ValueError:
        logging.debug('', exc_info=True) # this way it only shows up in debug mode
        pin.pin[PIN_HASHEXPENSE] = ''
        return

    if None in (eff, rate, poolfee, price, hv):
        pin.pin[PIN_HASHEXPENSE] = f''
        return

    fiat_pool_fee = poolfee * calcs.fiat(hv, price)
    ret = rate * (eff / 6000) * EXPECTED_BLOCKS_PER_DAY - fiat_pool_fee

    pin.pin[PIN_HASHEXPENSE] = f"$ {ret:,.5f}"

#####################################
def update_height( height ) -> None:
    h = get_entered_height()

    if h == None:
        return

    # only try to update the price if we're going at least one day back
    #if h < (config.height - 144):
    if h < config.height:
        #output.toast("ok, we're running a historial calculation!!!")
        output.toast("Using historical data") #, position=output.OutputPosition.TOP, scope='main')
        update_price()

    update_difficulty()
    update_timestamp()

    update_numbers()

###############################################
def update_numbers( throw_away=None ) -> None:
    """
        This is the callback for (just about) every 'pin' input field.  Why?
            Because this all-in-one function ensures that every field is updated whenever the user presses a key on the keyboard.
            All input fields are always up-to-date with proper numbers
    """

    #update_timestamp()
    #update_difficulty()
    update_subsity()
    update_hashrate()
    update_hashvalue()
    update_hashprice()
    update_cost() # really, just the help_text bit of it
    update_satsperth()
    update_fiatperth()
    update_eff()
    update_resell()
    update_hashexpense()
