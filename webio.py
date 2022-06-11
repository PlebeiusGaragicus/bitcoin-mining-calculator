# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

"""
This module contains the callbacks to the pywebio fields and
a lot of the code that runs the pywebio user interface
"""

import logging

from pywebio import pin
from pywebio import output

from constants import *
from nodes import *
from popups import *
from data import *
from calcs import *


# the number of projections that we've run.
# so we can increment the number when they are all displayed.
analysisnumber = 0


###############################
def show_projection():
    """
        THIS FUNCTION TAKES THE VALUES FROM THE INPUT FIELDS AND RUNS THE PROJECTION...
        TODO - I HAVE TO FUCKING SANITIZE THE INPUTS!!!!!!! DO IT ALL AT-ONCE HERE!
    """

    logging.info("show_projection()")

    try:
        hashrate = float(pin.pin[PIN_HASHRATE])
        wattage = int(pin.pin[PIN_WATTAGE])
        capex = float(pin.pin[PIN_COST])
        opex = float(pin.pin[PIN_OPEX])
        poolfee = float(pin.pin[PIN_POOLFEE] / 100)
        rate = float(pin.pin[PIN_KWH_RATE])
    except Exception as e:
        logging.debug("", exc_info=True)
        output.toast("Something went wrong - make sure you didn't leave anything blank!")
        return

    nh = float(pin.pin[PIN_NETWORKHASHRATE])

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




    #TODO SANITIZE INPUT - do a better job
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
    # # oh... and ALSO the sliders right below them
    # pin.pin[PIN_CAPEX] = pin.pin['play_with_capex'] = round(result['cost'] / result['hashrate'], 2) #TODO warning... I'm rounding numbers
    # pin.pin[PIN_EFF] = pin.pin['play_with_eff'] = round(result['wattage'] / result['hashrate'], 2)

    # # TODO - this will cause a bug... don't set to DEFAULT_P below... have another way!  Unless we make sure this function is only called once... and the value isn't reset???  Hmmm...
    # capexsatsperthpermonth = us.total_capex() / pin.pin[PIN_MONTHSTOPROJECT] / us.total_terahash()
    # capex /= m



    # PRINT EVERYTHING TO THE SCREEN...
    with output.use_scope('projection', clear=True):
        output.put_markdown( "# PROJECTION SUMMARIES:" )

    output.toast("re-calculating...", color='warn', duration=1)
    ## ACTUALLY DO THE CALCULATIONS
    res = calculate_projection(
        months=m,
        height=height,
        avgfee=avgfee,
        hashrate=hashrate,
        wattage=wattage,
        price=price,
        pricegrow=pricegrow,
        pricegrow2=pricegrow2,
        pricelag=pl,
        networh_hashrate=nh,
        hashgrow=hg,
        kWh_rate=0,
        #hashgrow2=hg2,
        opex=opex,
        capex=capex,
        resale_upper=0,
        resale_lower=0,
        poolfee=poolfee,
    )
    output.toast("done.", color='success', duration=1)

    table = make_table_string(res)

    global analysisnumber
    analysisnumber += 1

    # SHOW GRAPH
    with output.use_scope("result"):
        output.put_collapse(title=f"analysis #{analysisnumber}", content=[
            output.put_html( pretty_graph(res) ),
            output.put_collapse("Monthly Breakdown Table", content=[
            output.put_markdown( table ),
            output.put_table(tdata=[[
                    output.put_file('projection.csv', content=b'123,456,789'),
                    output.put_text("<<-- Download results as CSV file")
                ]])
        ])
        ], position=output.OutputPosition.TOP, open=True)
    #output.scroll_to('projection', position=output.Position.TOP)



#######################
def show_settings():
    with output.use_scope("settings", clear=True):

        output.put_markdown('## Mining equipment purchase consideration')

        output.put_table([[
                pin.put_input(name=PIN_WATTAGE, type='float', label="Wattage"),
                pin.put_input(name=PIN_HASHRATE, type='float', label='Hashrate (in terahash)'),
                pin.put_input(name=PIN_EFF, type='float', label="Efficiency (W/TH)", readonly=True),
                pin.put_slider(name=PIN_EFF_SLIDER, value=0,min_value=1, max_value=170, label="efficiency slider")
            ],[
                pin.put_input(name=PIN_BOUGHTATPRICE, type='float', label='bitcoin price at time of purchase', value=pin.pin[PIN_BTC_PRICE_NOW]),
                pin.put_input(name=PIN_COST, type='float', label='Dollar cost of machine'),
                pin.put_input(name=PIN_SAT_PER_TH, type='float', label="Sats per TH", readonly=True),
                pin.put_slider(name=PIN_COST_SLIDER, value=0,min_value=1, max_value=20_000, step=5, label="purchase amount slider")
            ]])
        pin.pin_on_change(name=PIN_BOUGHTATPRICE, onchange=boughtatprice_waschanged)
        pin.pin_on_change(name=PIN_COST, onchange=cost_waschanged)
        pin.pin_on_change(name=PIN_HASHRATE, onchange=hashrate_waschanged)
        pin.pin_on_change(name=PIN_WATTAGE, onchange=wattage_waschanged)
        pin.pin_on_change(name=PIN_COST_SLIDER, onchange=cost_slider)
        pin.pin_on_change(name=PIN_EFF_SLIDER, onchange=eff_slider)

        #output.put_button("Analyze Miner", onclick=updateminerdata, color='success')

        output.put_markdown("## Equipment resale / Depreciation Recapture")
        output.put_table([[
                pin.put_input(name=PIN_MONTHSTOPROJECT, type='number', value=DEFAULT_MONTHSTOPROJECT, label='Months until you re-sell this miner', help_text="Months to run projection"),
                pin.put_checkbox(name=PIN_NEVERSELL, options=[OPTION_NEVERSELL], value=False)
            ],[
                pin.put_input(name=PIN_RESELL_UPPER, type='number', value=75, label="Resale % UPPER limit", help_text="% percent of purchase price"),
                pin.put_input(name=PIN_UPPER_READONLY, type='number', label="Resale value UPPER LIMIT", readonly=True, help_text="($) resale amount")
            ],[
                pin.put_input(name=PIN_RESELL_LOWER, type='number', value=50, label="Resale % LOWER limit", help_text="% percent of purchase price"),
                pin.put_input(PIN_LOWER_READONLY, type='number', label="Resale value LOWER LIMIT", readonly=True, help_text="($) resale amount")
        ]])
        pin.pin_on_change(name=PIN_NEVERSELL, onchange=neversell_waschanged)
        pin.pin_on_change(PIN_RESELL_UPPER, onchange=upperresale_waschanged)
        pin.pin_on_change(PIN_RESELL_LOWER, onchange=lowerresale_waschanged)

        output.put_markdown("---")
        output.put_markdown("## Bitcoin network state")

        output.put_table([[
            #pin.put_input(name=PIN_BTC_PRICE_NOW, type='float', value=pin.pin[PIN_BTC_PRICE_NOW], label="Bitcoin price $"),
            pin.put_input(name=PIN_BTC_PRICE_NOW, type='float', label="Bitcoin price $"),
            #pin.put_input(name=PIN_HEIGHT, type='float', value=pin.pin[PIN_HEIGHT], label="blockchain height"),
            pin.put_input(name=PIN_HEIGHT, type='float', label="blockchain height"),
            #pin.put_input(name=PIN_NETWORKHASHRATE, type='float', value=pin.pin[PIN_NETWORKHASHRATE], label="network hashrate"),
            pin.put_input(name=PIN_NETWORKHASHRATE, type='float', label="network hashrate"),
            ],[
            #pin.put_input(name=PIN_AVERAGEFEE, type='float', value=pin.pin[PIN_AVERAGEFEE], label="average transaction fees per block", help_text=f"= {pin.pin[PIN_AVERAGEFEE] / ONE_HUNDRED_MILLION:.3f} bitcoin"),
            pin.put_input(name=PIN_AVERAGEFEE, type='float', label="average transaction fees per block"),
            output.put_button("block fee analysis", onclick=feeanalysis)
            ]
        ])
        pin.pin_on_change(name=PIN_AVERAGEFEE, onchange=avgfee_waschanged)

        output.put_markdown("---")
        output.put_markdown("## Cost-of-production variables")
        output.put_table([[
            pin.put_input(PIN_KWH_RATE, type='float', value= DEFAUL_KPKWH, label='your cost per kilowatt-hour: $'),
            pin.put_input(PIN_POOLFEE, type='float', value= DEFAULT_POOL_FEE, label='mining pool fee: %'),
            pin.put_input(PIN_OPEX, type='float', value= DEFAULT_OPEX, label='monthly operational cost: $'),
        ]])

        output.put_markdown("---")
        output.put_markdown("## Projection Parameters")

        output.put_table([[
            pin.put_input(name=PIN_PRICEGROW, type='float', value=DEFAULT_PRICEGROW, label='Monthly price growth: %', help_text='how fast do you predict the bitcoin price will grow month-to-month?'),
            pin.put_slider(PIN_PRICEGROW_SLIDER, label='Price growth slider', value=DEFAULT_PRICEGROW,min_value=-10.0, max_value=20.0, step=0.1),
            output.put_button("price history analysis", onclick=pricehistory)
            ],[
            pin.put_input(name=PIN_PRICEGROW2, type='float', value=DEFAULT_PRICEGROW2, label='Post-halvening price growth: %', help_text="How fast do you think the price will grow monthly post-halvening (and post 'lag')"),
            pin.put_slider(name="post_halvening_slider", label='Price growth slider', value=DEFAULT_PRICEGROW2,min_value=-10.0, max_value=20.0, step=0.1),
            pin.put_input(name=PIN_LAG, type='float', value=DEFAULT_LAG, label='Halvening price lag (months)', help_text="The price growth post-halvening sometimes lags a few months...")
            ],[
            pin.put_input(name=PIN_HASHGROW, type='float', value=DEFAULT_HASHGROW, label='Monthly hashrate growth: %'),
            pin.put_slider(PIN_HASHGROW_SLIDER, value=DEFAULT_HASHGROW,min_value=-2.0, max_value=10.0, step=0.1),
            output.put_button("hashrate history analysis", onclick=hashratehistory)
            ]
        ])
        pin.pin_on_change(PIN_PRICEGROW_SLIDER, onchange=pricegrow_slider)
        pin.pin_on_change(name=PIN_PRICEGROW2_SLIDER, onchange=pricegrow2_slider)
        pin.pin_on_change(PIN_HASHGROW_SLIDER, onchange=hashgrow_slider)
        pin.pin_on_change(name=PIN_HASHGROW, onchange=hashgrow_waschanged)

        #pin.put_checkbox('verbose', options=['VERBOSE MODE - (put every variable on the spreadsheet)'], inline=True)

        output.put_button( 'RUN PROJECTION', onclick=show_projection, color='warning' )





# THESE FUNCTIONS ARE CALLED BY THE SLIDER PIN CALLBACK AND ADJUST THE PIN INPUT THEY CORRESPOND
def pricegrow_slider( v: float ):
    try:
        pin.pin[PIN_PRICEGROW] = round(v, 2)
    except Exception as e:
        logging.debug("", exc_info=True)
        output.toast("Price growth metric can't be blank.")
        return
    show_projection()

def pricegrow2_slider( v: float ):
    try:
        pin.pin[PIN_PRICEGROW2] = round(v, 2)
    except Exception as e:
        logging.debug("", exc_info=True)
        output.toast("Post-halvening price growth metric can't be blank.")
        return
    show_projection()

def hashgrow_slider( v: float ):
    try:
        pin.pin[PIN_HASHGROW] = round(v, 2)
    except Exception as e:
        logging.debug("", exc_info=True)
        output.toast("Hash growth metric can't be blank")
        return
    show_projection()

def eff_slider( v: float ):
    """
        THIS IS THE CALLBACK FOR THE SLIDER
        THE SLIDER MEASURES EFF...
            SO WHEN IT'S UPDATED WE UPDATE HASHRATE ASSUME A CONSTANT WATTAGE
    """
    try:
        hr = round(pin.pin[PIN_WATTAGE] / v, 2)
        pin.pin[PIN_HASHRATE] = hr
        pin.pin[PIN_EFF] = round(v, 2)

        usd_cost_of_miner = pin.pin[PIN_COST]
        boughtatprice = pin.pin[PIN_BOUGHTATPRICE]
        dollarsperth =  usd_cost_of_miner / hr

        if None in [usd_cost_of_miner, dollarsperth, boughtatprice]:
            pin.pin_update(PIN_SAT_PER_TH, help_text='')
            pin.pin[PIN_SAT_PER_TH] = ''
            return

        pin.pin_update(PIN_SAT_PER_TH, help_text=f"${dollarsperth:,.2f} / TH")
        pin.pin[PIN_SAT_PER_TH] = f"{round(btc(usd_cost_of_miner, price=boughtatprice) / hr, 1):,.2f}"
    except Exception as e:
        logging.debug("", exc_info=True)
        output.toast("Enter in mining equipment details first.")
        return
    #show_projection()

def hashrate_waschanged(hashrate: float):
    """
        THIS IS THE CALLBACK FOR PIN_HASHRATE ONCHANGE=
        it updates PIN_EFF and PIN_EFF_SLIDER slider
    """
    if hashrate == None:
        return

    if not pin.pin[PIN_WATTAGE] == None and pin.pin[PIN_WATTAGE] >= 1:
        pin.pin[PIN_EFF] = pin.pin[PIN_EFF_SLIDER] = round(pin.pin[PIN_WATTAGE] / hashrate, 2)

    if hashrate == None or hashrate < 1:
        pin.pin[PIN_EFF] = pin.pin[PIN_EFF_SLIDER] = 0
        return

    usd_cost_of_miner = pin.pin[PIN_COST]
    
    if not usd_cost_of_miner == None:
        dollarsperth = usd_cost_of_miner / hashrate
        pin.pin_update(PIN_SAT_PER_TH, help_text=f"${dollarsperth:,.2f} / TH")

        boughtatprice = pin.pin[PIN_BOUGHTATPRICE]
        if not boughtatprice == None:
            pin.pin[PIN_SAT_PER_TH] = round(ONE_HUNDRED_MILLION * (usd_cost_of_miner/boughtatprice) / hashrate, 2)

def wattage_waschanged(wattage: float):
    """
        THIS IS THE CALLBACK FOR PIN_WATTAGE ONCHANGE=
        it updates PIN_EFF and PIN_EFF_SLIDER slider
    """
    if wattage == None or wattage < 1:
        pin.pin[PIN_EFF] = pin.pin[PIN_EFF_SLIDER] = 0
        return

    if pin.pin[PIN_HASHRATE] == None or pin.pin[PIN_HASHRATE] < 1:
        return

    pin.pin[PIN_EFF] = pin.pin[PIN_EFF_SLIDER] = round(wattage / pin.pin[PIN_HASHRATE], 1)


def cost_slider(usd_cost_of_miner: float):
    try:
        hr = float(pin.pin[PIN_HASHRATE])
        dollarsperth = usd_cost_of_miner / hr

        pin.pin_update(PIN_SAT_PER_TH, help_text=f"${dollarsperth:,.2f} / TH")
        pin.pin[PIN_COST] = round(usd_cost_of_miner, 2)

        # I don't like this... we aren't sanitizing
        upperresale_waschanged( pin.pin[PIN_RESELL_UPPER] )
        lowerresale_waschanged( pin.pin[PIN_RESELL_LOWER] )

        new_boughtatprice = float(pin.pin[PIN_BOUGHTATPRICE])
        pin.pin[PIN_SAT_PER_TH] = f"{round(btc(usd_cost_of_miner, price=new_boughtatprice) / hr, 1):,.2f}"
        pin.pin_update(name=PIN_COST, help_text=f"{ONE_HUNDRED_MILLION * (usd_cost_of_miner/new_boughtatprice):,.1f} sats")
        #pin.pin[PIN_SAT_PER_TH] = round(btc(usd_cost_of_miner, price=newprice) / hr, 1)
    except Exception as e:
        logging.debug("", exc_info=True)
        return

def boughtatprice_waschanged(newprice: float):
    if newprice == None or newprice < 1:
        pin.pin[PIN_SAT_PER_TH] = ''
        return

    try:
        usd_cost_of_miner = float(pin.pin[PIN_COST])
        hr = float(pin.pin[PIN_HASHRATE])
    except Exception as e:
        logging.debug("", exc_info=True)
        pin.pin[PIN_SAT_PER_TH] = ''
        pin.pin[PIN_COST_SLIDER] = ''
        return

    pin.pin[PIN_SAT_PER_TH] = f"{round(btc(usd_cost_of_miner, price=newprice) / hr, 1):,.2f}"
    pin.pin_update(name=PIN_COST, help_text=f"{ONE_HUNDRED_MILLION * (usd_cost_of_miner/newprice):,.1f} sats")
    #pin.pin[PIN_SAT_PER_TH] = round(btc(usd_cost_of_miner, price=newprice) / hr, 1)

    # call this to adjust everything else along with it
    # adjust_cost( float(pin.pin[PIN_COST]) )


def cost_waschanged(cost: float):
    # if pin.pin[PIN_WATTAGE] == None or pin.pin[PIN_WATTAGE] < 1:
    #     return
    # if hashrate == None or hashrate < 1:
    #     pin.pin[PIN_EFF] = pin.pin["play_with_eff"] = 0
    #     return

    # pin.pin[PIN_EFF] = pin.pin["play_with_eff"] = round(pin.pin[PIN_WATTAGE] / hashrate, 2)

    if cost == None or cost < 1:
        pin.pin[PIN_SAT_PER_TH] = ''
        pin.pin[PIN_COST_SLIDER] = ''
        pin.pin_update(name=PIN_COST, help_text='')
        pin.pin_update(PIN_UPPER_READONLY, value='')
        pin.pin_update(PIN_LOWER_READONLY, value='')
        return
    try:
        pin.pin[PIN_COST_SLIDER] = cost
        hr = float(pin.pin[PIN_HASHRATE])
        dollarsperth = cost / hr
        pin.pin_update(name=PIN_SAT_PER_TH, help_text=f"${dollarsperth:.1f} / TH")

        # again... I'm not a fan of this.. nothing is sanitized
        upperresale_waschanged( int(pin.pin[PIN_RESELL_UPPER]) )
        lowerresale_waschanged( int(pin.pin[PIN_RESELL_UPPER]) )

        btcuponpurchase = float(pin.pin[PIN_BOUGHTATPRICE])
    except Exception as e:
        logging.debug("", exc_info=True)
        return
    
    pin.pin_update(name=PIN_COST, help_text=f"{ONE_HUNDRED_MILLION * (cost/btcuponpurchase):,.1f} sats")
    pin.pin[PIN_SAT_PER_TH] = f"{round(btc(cost, price=btcuponpurchase) / hr, 1):,.2f}"

def neversell_waschanged( o ):
    if OPTION_NEVERSELL in o:
        # NEVER SELL
        pin.pin_update(name=PIN_RESELL_UPPER, readonly=True)
        pin.pin_update(name=PIN_RESELL_LOWER, readonly=True)
        pin.pin_update(name=PIN_MONTHSTOPROJECT, label="Expected machine life span")
    else:
        # WILL SELL
        pin.pin_update(name=PIN_RESELL_UPPER, readonly=False)
        pin.pin_update(name=PIN_RESELL_LOWER, readonly=False)
        pin.pin_update(name=PIN_MONTHSTOPROJECT, label="Months until you re-sell this miner")

def upperresale_waschanged(v: int):
    try:
        v = pin.pin[PIN_COST] * (pin.pin[PIN_RESELL_UPPER] / 100)
        pin.pin_update(PIN_UPPER_READONLY, value=v)
    except Exception as e:
        logging.debug("", exc_info=True)
        return

def lowerresale_waschanged(v: int):
    try:
        v = pin.pin[PIN_COST] * (pin.pin[PIN_RESELL_LOWER] / 100)
        pin.pin_update(PIN_LOWER_READONLY, value=v)
    except Exception as e:
        logging.debug("", exc_info=True)
        return
    pass

def hashgrow_waschanged( newval: float ):
    if newval == None:
        return
    
    # THIS DOES NOT WORK-Y WORK... :) SAD EMOJI GOES HERE
    #pin.pin_update(PIN_HASHGROW_SLIDER, max_value=int(newval*2))

    pin.pin_update(PIN_HASHGROW_SLIDER, value=newval)
    pin.pin[PIN_HASHGROW_SLIDER] = newval


def avgfee_waschanged( newval: float):
    if newval == None:
        n = ''
    else:
        n = newval / ONE_HUNDRED_MILLION
    pin.pin_update(name=PIN_AVERAGEFEE, help_text=f'{n:.2f} bitcoin')
