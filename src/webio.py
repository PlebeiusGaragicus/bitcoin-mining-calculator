# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This module contains the callbacks to the pywebio fields and
a lot of the code that runs the pywebio user interface
"""

import logging
from multiprocessing import pool

from pywebio import pin
from pywebio import output

import config
from constants import *
#from calcs import btc, fiat, make_table_string, pretty_graph, calculate_projection
import calcs
import popups

#######################
def show_projection():
    """
        THIS FUNCTION TAKES THE VALUES FROM THE INPUT FIELDS AND RUNS THE PROJECTION...
        TODO - SANITIZE THE INPUTS!
    """

    logging.info("running show_projection()")

    try:
        hashrate = float(pin.pin[PIN_HASHRATE])
        wattage = int(pin.pin[PIN_WATTAGE])
        capex = float(pin.pin[PIN_COST])
        opex = float(pin.pin[PIN_OPEX])
        poolfee = float(pin.pin[PIN_POOLFEE] / 100)
        rate = float(pin.pin[PIN_KWH_RATE])
    except TypeError as e:
        logging.exception('')
        output.toast("Something went wrong - Check all the input fields!")
        return

    #nh = float(pin.pin[PIN_NETWORKHASHRATE])
    diff = float(pin.pin[PIN_NETWORKDIFFICULTY])

    avgfee = float(pin.pin[PIN_AVERAGEFEE])

    height = int(pin.pin[PIN_HEIGHT])
    price = float(pin.pin[PIN_BTC_PRICE_NOW])

    # TODO fix this... make it a function that is easier and neater and less prone to mistakes.
    m = int(pin.pin[PIN_MONTHSTOPROJECT])
    hg = float(pin.pin[PIN_HASHGROW] / 100)
    #hg2 = float(pin.pin[PIN_HASHGROW2] / 100)
    hg2=0
    pricegrow = float(pin.pin[PIN_PRICEGROW] / 100)
    pricegrow2 = float(pin.pin[PIN_PRICEGROW2] / 100)
    pl = int(pin.pin[PIN_LAG])

    resale_upper = pin.pin[PIN_RESELL]


    #TODO SANITIZE INPUT - do a better job
    if pin.pin['wattage'] == None or pin.pin['wattage'] <= 0:
        output.toast("invalid wattage - no miners added")
        return
    if pin.pin['hashrate'] == None or pin.pin['hashrate'] <= 0:
        output.toast("invalid hashrate - no miners added")
        return
    if pin.pin[PIN_COST] == None or pin.pin[PIN_COST] <= 0:
        output.toast("invalid cost - no miners added")
        return
    if None in [m, pricegrow, hg]:
        output.toast("missing projection parameters...")
        output.toast("can't leave input field blank", color='error')
        return


    # # we convert the dollar cost to satoshis using the provided bitcoin price at time of equipment purchase
    # pin.pin[PIN_CAPEX] = btc( result['cost'], price=result['btcprice'])


    # # NOW WE HAVE TO CHANGE THE PIN INPUTS PIN_CAPEX AND PIN_EFF
    # pin.pin[PIN_CAPEX] = pin.pin['play_with_capex'] = round(result['cost'] / result['hashrate'], 2) #TODO warning... I'm rounding numbers
    # pin.pin[PIN_EFF] = pin.pin['play_with_eff'] = round(result['wattage'] / result['hashrate'], 2)

    # # TODO - this will cause a bug... don't set to DEFAULT_P below... have another way!  Unless we make sure this function is only called once... and the value isn't reset???  Hmmm...
    # capexsatsperthpermonth = us.total_capex() / pin.pin[PIN_MONTHSTOPROJECT] / us.total_terahash()
    # capex /= m

    price_when_bought = pin.pin[PIN_BOUGHTATPRICE]

    # PRINT EVERYTHING TO THE SCREEN...
    with output.use_scope('projection', clear=True):
        output.put_markdown( "# PROJECTION SUMMARIES:" )

    output.toast("calculating...", color='warn', duration=1)
    ## ACTUALLY DO THE CALCULATIONS
    res = calcs.calculate_projection(
        months = m,
        height = height,
        avgfee = avgfee,
        hashrate = hashrate,
        wattage = wattage,
        price = price,
        pricegrow = pricegrow,
        pricegrow2 = pricegrow2,
        pricelag = pl,
        #networh_hashrate=nh,
        network_difficulty = diff,
        hashgrow = hg,
        kWh_rate = rate,
        #hashgrow2=hg2,
        opex = opex,
        capex_in_sats = calcs.btc(capex, bitcoin_price=price_when_bought),
        resale_upper = resale_upper,
        poolfee = poolfee,
    )
    output.toast("done.", color='success', duration=1)

    table = calcs.make_table_string(res)

    config.analysis_number += 1

    # SHOW GRAPH
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

#######################
def show_user_interface_elements():

    output.put_markdown( MAIN_TEXT )
    output.put_collapse(title="TOOLS:", content=[
        output.put_button("fiat <-> bitcoin converter", onclick=popups.popup_currencyconverter, color='info'),
        output.put_button("break-even analysis", onclick=popups.popup_breakeven_analysis, color='info'),
        output.put_button("block fee analysis", onclick=popups.popup_fee_analysis)
    ])

    ### NETWORK STATE ### NETWORK STATE ### NETWORK STATE ### NETWORK STATE ### NETWORK STATE
    output.put_markdown("### Bitcoin network state")
    output.put_table([[
        pin.put_input(name=PIN_BTC_PRICE_NOW, type='float', label="Bitcoin price $", value=0),
        pin.put_input(name=PIN_HEIGHT, type='float', label="blockchain height", value=0),
        pin.put_input(name=PIN_AVERAGEFEE, type='float', label="average tx fee", value=0, help_text='in satoshi'),
        pin.put_input(name=PIN_SUBSIDY, type='text', label="total reward", value=0, readonly=True, help_text='in satoshi')
    ],[
        pin.put_input(name=PIN_NETWORKDIFFICULTY, type='float', label="network difficulty", value=0),
        pin.put_input(name=PIN_NETWORKHASHRATE, type='text', label="network TH/s", value=0, readonly=True),
        pin.put_input(name=PIN_HASHVALUE, type='text', label="hash value", value=0, readonly=True, help_text='satoshi earned per Terahash generated per day'),
        pin.put_input(name=PIN_HASHPRICE, type='text', label="hash price", value=0, readonly=True, help_text='hash value denominated in fiat at today\'s price')
        ]])
    pin.pin_on_change(name=PIN_BTC_PRICE_NOW, onchange=update_numbers)
    pin.pin_on_change(name=PIN_HEIGHT, onchange=update_numbers)
    pin.pin_on_change(name=PIN_AVERAGEFEE, onchange=update_numbers)
    pin.pin_on_change(name=PIN_NETWORKDIFFICULTY, onchange=update_numbers)

    # output.put_table([[
    #     ]])
    
    ### MINER SPECIFICATION ### MINER SPECIFICATION ### MINER SPECIFICATION ### MINER SPECIFICATION ### MINER SPECIFICATION 
    output.put_markdown('### hardware specification / capital expenditure')
    output.put_table([[
            pin.put_input(name=PIN_BOUGHTATPRICE, type='float', label='bitcoin price at time of purchase', value=pin.pin[PIN_BTC_PRICE_NOW]),
            pin.put_input(name=PIN_COST, type='float', label='Dollar cost of machine'),
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
            pin.put_input(name=PIN_EFF, type='float', label="Efficiency (W/TH)", readonly=True)
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

    output.put_markdown("---")
    output.put_markdown("### Cost-of-production")
    output.put_table([[
        pin.put_input(PIN_KWH_RATE, type='float', label='cost per kilowatt-hour: $', value=DEFAUL_KPKWH),
        pin.put_input(PIN_POOLFEE, type='float', label='mining pool fee: %', value= DEFAULT_POOL_FEE),
        pin.put_input(PIN_HASHEXPENSE, type='float', label='hash expense', value=0, readonly = True, help_text='your cost-of-production per Terahash per day'),
        pin.put_input(PIN_OPEX, type='float', label='monthly operational cost: $', value= DEFAULT_OPEX)
    ]])
    pin.pin_on_change(PIN_KWH_RATE, onchange=update_numbers)
    pin.pin_on_change(PIN_OPEX, onchange=update_numbers)
    pin.pin_on_change(PIN_POOLFEE, onchange=update_numbers)

    output.put_markdown("---")
    output.put_markdown("### Projection Parameters")

    output.put_table([[
        pin.put_input(name=PIN_PRICEGROW, type='float', value=DEFAULT_PRICEGROW, label='Monthly price growth: %', help_text='how fast do you predict the bitcoin price will grow month-to-month?'),
        #pin.put_slider(PIN_PRICEGROW_SLIDER, label='Price growth slider', value=DEFAULT_PRICEGROW,min_value=-10.0, max_value=20.0, step=0.1),
        output.put_button("price history analysis", onclick=popups.popup_price_history)
        ],[
        pin.put_input(name=PIN_PRICEGROW2, type='float', value=DEFAULT_PRICEGROW2, label='Post-halvening price growth: %', help_text="How fast do you think the price will grow monthly post-halvening (and post 'lag')"),
        #pin.put_slider(name="post_halvening_slider", label='Price growth slider', value=DEFAULT_PRICEGROW2,min_value=-10.0, max_value=20.0, step=0.1),
        pin.put_input(name=PIN_LAG, type='float', value=DEFAULT_LAG, label='Halvening price lag (months)', help_text="The price growth post-halvening sometimes lags a few months...")
        ],[
        pin.put_input(name=PIN_HASHGROW, type='float', value=DEFAULT_HASHGROW, label='Monthly hashrate growth: %'),
        #pin.put_slider(PIN_HASHGROW_SLIDER, value=DEFAULT_HASHGROW,min_value=-2.0, max_value=10.0, step=0.1),
        output.put_button("hashrate history analysis", onclick=popups.popup_difficulty_history)
        ]
    ])
    #pin.pin_on_change(PIN_PRICEGROW_SLIDER, onchange=pricegrow_slider)
    #pin.pin_on_change(name=PIN_PRICEGROW2_SLIDER, onchange=pricegrow2_slider)
    #pin.pin_on_change(PIN_HASHGROW_SLIDER, onchange=hashgrow_slider)
    #pin.pin_on_change(name=PIN_HASHGROW, onchange=hashgrow_waschanged)

    output.put_button( 'RUN PROJECTION', onclick=show_projection, color='warning' )


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
        ret =  float(pin.pin[PIN_POOLFEE] / 1000)
    except TypeError:
        logging.debug('mining pool fee - input field blank', exc_info=True)
        return None

    if ret < 0.00:
        return None
    return ret


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









##############################
def update_subsity() -> None:
    height = get_entered_height()
    fees = get_entered_fees()

    if None in (height, fees):
        pin.pin[PIN_SUBSIDY] = ''
        return

    total = calcs.block_subsity( height ) + fees

    pin.pin[PIN_SUBSIDY] = f"{total:,}"

###############################
def update_hashrate() -> None:
    diff = get_entered_difficulty()

    if None in (diff, 0): # this is lame... I am lame for writing this... but this make the code consistant... and it works... so buzz off
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

    nh = round(calcs.get_hashrate_from_difficulty(diff), 2)
    reward = calcs.block_subsity( height ) + fees
    r = reward / nh * EXPECTED_BLOCKS_PER_DAY

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

    dollars_per_th = cost / hashrate

    # dollarsperth = cost / hashrate # uncaught DivideByZeroError
    #pin.pin[PIN_FIAT_PER_TH] = f"${dollarsperth:,.2f} / TH"
    pin.pin[PIN_FIAT_PER_TH] = f"{dollars_per_th:,.2f}"

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
        hp = float(str(pin.pin[PIN_HASHPRICE]).replace('$ ', ''))
    except ValueError:
        logging.debug('', exc_info=True) # this way it only shows up in debug mode
        pin.pin[PIN_HASHEXPENSE] = ''
        return

    if None in (eff, rate, poolfee, price, hp):
        pin.pin[PIN_HASHEXPENSE] = f''
        return

    fiat_pool_fee = poolfee * calcs.fiat(hp, price)
    ret = rate * (eff / 6000) * EXPECTED_BLOCKS_PER_DAY - fiat_pool_fee

    pin.pin[PIN_HASHEXPENSE] = f"$ {ret:,.5f}"




###############################################
def update_numbers( throw_away=None ) -> None:
    """
        This is the callback for (just about) every 'pin' input field.  Why?
            Because this all-in-one function ensures that every field is updated whenever the user presses a key on the keyboard.
            All input fields are always up-to-date with proper numbers
    """

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
















# pin.pin[PIN_SAT_PER_TH] = f"{round(btc(usd_cost_of_miner, bitcoin_price=newprice) / hr, 1):,.2f}"
# pin.pin_update(name=PIN_COST, help_text=f"{ONE_HUNDRED_MILLION * (usd_cost_of_miner/newprice):,.1f} sats")
# #pin.pin[PIN_SAT_PER_TH] = round(btc(usd_cost_of_miner, price=newprice) / hr, 1)

# if cost == None or cost < 1:
#     pin.pin[PIN_SAT_PER_TH] = ''
#     pin.pin_update(name=PIN_COST, help_text='')
#     pin.pin_update(PIN_RESELL_READONLY, value='')
#     return

# hr = float(pin.pin[PIN_HASHRATE])
# dollarsperth = cost / hr
# pin.pin_update(name=PIN_SAT_PER_TH, help_text=f"${dollarsperth:.1f} / TH")



# btcuponpurchase = float(pin.pin[PIN_BOUGHTATPRICE])

# pin.pin_update(name=PIN_COST, help_text=f"{ONE_HUNDRED_MILLION * (cost/btcuponpurchase):,.1f} sats")
# pin.pin[PIN_SAT_PER_TH] = f"{round(btc(cost, bitcoin_price=btcuponpurchase) / hr, 1):,.2f}"






# ####################################
# def upperresale_waschanged(v: int):
#     try:
#         v = pin.pin[PIN_COST] * (pin.pin[PIN_RESELL] / 100)
#         pin.pin_update(PIN_RESELL_READONLY, value=v)
#     except Exception as e:
#         logging.debug("", exc_info=True)
#         return

# #######################################
# def avgfee_waschanged( newval: float):
#     if newval == None:
#         n = ''
#     else:
#         n = newval / ONE_HUNDRED_MILLION
#     pin.pin_update(name=PIN_AVERAGEFEE, help_text=f'{n:.2f} bitcoin')






# if not usd_cost_of_miner == None:
#     dollarsperth = usd_cost_of_miner / hashrate
#     pin.pin_update(PIN_SAT_PER_TH, help_text=f"${dollarsperth:,.2f} / TH")

#     boughtatprice = pin.pin[PIN_BOUGHTATPRICE]
#     if not boughtatprice == None:
#         pin.pin[PIN_SAT_PER_TH] = round(ONE_HUNDRED_MILLION * (usd_cost_of_miner/boughtatprice) / hashrate, 2)

# if newprice == None or newprice < 1:
#     pin.pin[PIN_SAT_PER_TH] = ''
#     return

# try:
#     usd_cost_of_miner = float(pin.pin[PIN_COST])
#     hr = float(pin.pin[PIN_HASHRATE])
# except Exception as e:
#     #logging.debug("", exc_info=True)
#     pin.pin[PIN_SAT_PER_TH] = ''
#     return
# upperresale_waschanged( int(pin.pin[PIN_RESELL]) )
