# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
This module is used to actually do the cool calculations ;)
"""

import logging

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from constants import *

####################################
def block_subsity( height ) -> int:
    """
        This returns the coinbase reward in satoshi for a given block height

        see: https://github.com/bitcoin/bitcoin/blob/b71d37da2c8c8d2a9cef020731767a6929db54b4/src/validation.cpp#L1479-L1490
    """
    return (50 * ONE_HUNDRED_MILLION) >> (height // SUBSIDY_HALVING_INTERVAL)

#################################################
def blocks_until_halvening(block_height) -> int:
    """
        This tells you how many blocks until the next halvening
    """
    return ((block_height // SUBSIDY_HALVING_INTERVAL + 1) * SUBSIDY_HALVING_INTERVAL) - block_height


########################################
def fiat(sats, bitcoin_price) -> float:
    """
        Convert sats into fiat value at given price of bitcoin
    """
    return sats * (bitcoin_price / ONE_HUNDRED_MILLION)

#######################################
def btc(fiat, bitcoin_price) -> float:
    """
        Convert fiat into sats at given price of bitcoin
    """
    return int(ONE_HUNDRED_MILLION * (fiat / bitcoin_price))


###################################################
def hash_value(subsidy, fees, difficulty) -> float:
    """
        This will return the hash value
    """
    nh = get_hashrate_from_difficulty(difficulty)

    return (subsidy + fees) / nh

###########################
def hash_price() -> float:
    raise NotImplementedError
    return 0.0

########################################
def get_difficulty(bits: int) -> float:
    """
        This converts the 'bits' field in a bitcoin block to the 'difficulty' number
        reference: https://github.com/bitcoin/bitcoin/blob/8f3ab9a1b12a967cd9827675e9fce112e51d42d8/src/rpc/blockchain.cpp#L75-L95
    """

    shift = (bits >> 24) & 0xFF
    diff = 0x0000FFFF / (bits & 0x00FFFFFF)

    while shift < 29:
        diff *= 256.0
        shift += 1
    
    while shift > 29:
        diff /= 256.0
        shift -= 1

    return diff

###############################################################
def get_hashrate_from_difficulty( difficulty: float) -> float:
    """
        Returns estimated network terahashes for a given network difficulty
    """
    return (difficulty * 2 ** 32) / 600 / TERAHASH

##########################
def calculate_projection(
                        months, height, avgfee, hashrate, wattage,
                        price, pricegrow, pricegrow2, pricelag,
                        network_difficulty, hashgrow,
                        kWh_rate, opex,capex_in_sats, resale, poolfee
                    ) -> dict:
    """
        This function taken in all variables of interest and projects bitcoin earnings and fiat cost of running bitcoin miners

        This function returns a dict with the projection results.
    """

    res = {
        # THESE ARE THE INPUTS TO THE CALCULATION
        KEY_MONTHS_TO_PROJECT : months,
        KEY_START_HEIGHT : height,
        KEY_AVGFEE : avgfee,
        KEY_MY_HASHRATE : hashrate,
        KEY_WATTAGE : wattage,
        KEY_START_PRICE : price,
        KEY_PRICE_GROWTH : pricegrow,
        KEY_PRICE_GROWTH2 : pricegrow2,
        KEY_PRICE_LAG : pricelag,
        KEY_HASH_GROWTH : hashgrow,
        KEY_MONTHLY_OPEX : opex,
        KEY_CAPEX_SATS : capex_in_sats, # sats
        KEY_RESALE : resale,
        KEY_POOLFEE : poolfee, # whole number percent / need to divide by 100
        KEY_RATE_KWH : kWh_rate,
        # THE REST OF THESE BELOW ARE CALCULATED OFF OF THE ABOVE GIVEN VARIABLES
        #HEIGHT AT THE END OF THE MONTH!
        KEY_ESTIMATED_HEIGHT : [],
        KEY_ESTIMATED_NETWORK_HASHRATE : [],
        KEY_ESTIMATED_PRICE : [],
        #KEY_ESTIMATED_AVGFEE : [],
        # EARNED
        KEY_HASHVALUE : [],
        # BURNED
        KEY_KWH : [],
        # THE SATS SOLD EVERY MONTH TO COVER THE GIVEN EXPENSE
        KEY_SOLD_ELECTRICITY : [],
        KEY_SOLD_OPEX : [],
        KEY_SOLD_CAPEX : [],
        # DECISION / FOREWARD-LOOKING // PROFIC ASSUMPTION MAKING-DECISION POINTS
        KEY_BREAKEVEN_PRICE : [], # at current nh
        KEY_BREAKEVEN_PRICE_P20P : [], # plus 20% 'worth my time fee', at current nh
        KEY_BREAKEVEN_NH : [], # at estimated price
    }

    if None in (months,height, avgfee, hashrate, wattage, price,
                pricegrow, pricegrow2, pricelag, network_difficulty,
                hashgrow, kWh_rate, opex, capex_in_sats, resale, poolfee):
        logging.error("None variable passed to calculate_projection()")
        return

    networh_hashrate = get_hashrate_from_difficulty(network_difficulty)

    capexsats_per_months = capex_in_sats / months
    logging.debug(f"capex: {capex_in_sats} sats -> {capexsats_per_months} sats/month")

    capex_in_sats *= 1 - (resale / 100)
    logging.debug(f"resell: {resale}% -> {capex_in_sats} sats/month")

    capexsats_per_months = capex_in_sats / months
    logging.debug(f"capex: {capex_in_sats} sats -> {capexsats_per_months} sats/month")

    # have we crossed a halvening?  We use this to determine which growth factor to use with price/nh
    # TODO - what if we project out really far and cross TWO halvenings?
    crossed = False
    # this used in conjunction with pricelag
    month_we_crossed = 0

    for m in range(months):
        sats_earned = 0
        #poolfee = 0
        _kwh = 0

        # DO ONE DAY OF CALCULATIONS
        for _day in range(30):

            if blocks_until_halvening( height ) < EXPECTED_BLOCKS_PER_DAY:
                crossed = True
                month_we_crossed = m

                # GO BLOCK BY BLOCK
                for _blk in range( EXPECTED_BLOCKS_PER_DAY ):

                    sats_earned += hashrate * (block_subsity( height ) + avgfee) * (1 - poolfee) / networh_hashrate
                    _kwh += wattage / 6000
                    height += 1

                    #logging.debug(f"block - block {height}, subsidy {block_subsity( height )}, nh {networh_hashrate/MEGAHASH:,.2f}, kWh {_kwh}")

            # DO A WHOLE DAY AT A TIME
            else:
                sats_earned += hashrate * (block_subsity( height ) + avgfee) * (1 - poolfee) * EXPECTED_BLOCKS_PER_DAY / networh_hashrate
                _kwh += 24 * wattage / 1000
                height += EXPECTED_BLOCKS_PER_DAY

                #logging.debug(f"day - block {height}, subsidy {block_subsity( height )}, nh {networh_hashrate/MEGAHASH:,.2f}, kWh {_kwh}")

            # END OF DAY STUFF
            networh_hashrate *= 1 + hashgrow / 30

        # END OF MONTH STUFF - now we have to settle

        # if we have crossed the halvening AND it's been 'LAG MONTHS' since... use pricegrow2
        if crossed and m - month_we_crossed >= pricelag:
            price *= 1 + pricegrow2
            #logging.debug(f"price increased to {price} - using growth factor2: {pricegrow2}")
        else:
            # if we haven't crossed a halvening... OR it hasn't been 'LAG MONTHS' yet
            price *= 1 + pricegrow # 1 + pricegrow / 30 # daily
            #logging.debug(f"price increased to {price} - using growth factor2: {pricegrow2}")

        sold_e = btc(_kwh * kWh_rate, bitcoin_price=price)
        sold_o = btc(opex, bitcoin_price=price) # we divide opex by my hashrate because everything else on this graph is reduced in this manner

        # basically, just the decision/assumption-making/verifying helper variables
        breakeven_price = ((ONE_HUNDRED_MILLION * opex) + (ONE_HUNDRED_MILLION * _kwh * kWh_rate)) / (sats_earned - btc(capex_in_sats, bitcoin_price=price))

        res[KEY_ESTIMATED_HEIGHT].append( height )
        res[KEY_ESTIMATED_NETWORK_HASHRATE].append( networh_hashrate )
        res[KEY_ESTIMATED_PRICE].append( price )
        #res[KEY_ESTIMATED_AVGFEE].append( 0 )

        res[KEY_HASHVALUE].append( sats_earned )
        res[KEY_KWH].append( _kwh )

        res[KEY_SOLD_ELECTRICITY].append( sold_e )
        res[KEY_SOLD_OPEX].append( sold_o )
        res[KEY_SOLD_CAPEX].append( capexsats_per_months )

        res[KEY_BREAKEVEN_PRICE].append( breakeven_price )
        # KEY_BREAKEVEN_PRICE_P20P : [],
        # KEY_BREAKEVEN_NH : [],
    return res

#######################
def pretty_graph(res):
    """
        this takes the projection results (returned by calculate_projection() and returns a pretty graph
    """
    #fig = go.Figure()
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=[*range( len(res[KEY_HASHVALUE]) ), res[KEY_ESTIMATED_HEIGHT]],
            #y=res[KEY_SATS_SOLD],
            # make these negative numbers... ;)
            #y=[round(e, 1) for e in res[KEY_SATS_SOLD]],
            y=res[KEY_HASHVALUE],
            name="sats earned",
            line_color="#A50CAC" # PURPLE
        ), secondary_y=False)
    fig.add_trace(
        go.Bar(
            x=[*range( len(res[KEY_SOLD_CAPEX]) )],
            #y=res[KEY_SATS_SOLD],
            # make these negative numbers... ;)
            #y=[round(e, 1) for e in res[KEY_SATS_SOLD]],
            #y=res[KEY_SOLD_OPEX],
            y=[round(e, 1) for e in res[KEY_SOLD_CAPEX]],
            name="sats sold for CAPEX",
            #color="#07A154" # GREEN
            #choropleth='#07A154'
            #https://plotly.com/python/bar-charts/#colored-bars
            #pattern_shape="nation", pattern_shape_sequence=[".", "x", "+"])
        ), secondary_y=False)
    fig.add_trace(
        go.Bar(
            x=[*range( len(res[KEY_SOLD_OPEX]) )],
            #y=res[KEY_SATS_SOLD],
            # make these negative numbers... ;)
            #y=[round(e, 1) for e in res[KEY_SATS_SOLD]],
            #y=res[KEY_SOLD_OPEX],
            y=[round(e, 1) for e in res[KEY_SOLD_OPEX]],
            name=f"sats sold for OPEX - ${DEFAULT_OPEX}",
        ), secondary_y=False)

    fig.add_trace(
        go.Bar(
            x=[*range( len(res[KEY_SOLD_ELECTRICITY]) )],
            #y=res[KEY_SATS_SOLD],
            # make these negative numbers... ;)
            #y=[round(e, 1) for e in res[KEY_SATS_SOLD]],
            #y=res[KEY_SOLD_ELECTRICITY],
            y=[round(e, 1) for e in res[KEY_SOLD_ELECTRICITY]],
            name="sats sold for ELECTRICITY"
        ), secondary_y=False)

    # CALCULATED BREAK-EVEN PRICE
    fig.add_trace(
        go.Scatter(
            x=[*range( len(res[KEY_BREAKEVEN_PRICE]) )],
            y=res[KEY_BREAKEVEN_PRICE],
            name="Break-even Bitcoin price",
            line_color="#CBDE12" # YELLOW
        ), secondary_y=True,)
    # THE PRICE WE ESTIMATE/FORECAST
    fig.add_trace(
        go.Scatter(
            x=[*range( len(res[KEY_ESTIMATED_PRICE]) )],
            y=[round(e, 1) for e in res[KEY_ESTIMATED_PRICE]],
            name="Predicted Bitcoin price",
            line_color="#12DE4D" # LIGHT GREEN
        ), secondary_y=True)

    # hodld = []
    # for i in range(len(res[KEY_SATS_EARNED])):
    #     hodld.append( round(res[KEY_SATS_EARNED][i] - res[KEY_SATS_SOLD][i], 1))

    # fig.add_trace(
    #     go.Bar(
    #         x=[*range( len(res[KEY_SATS_EARNED]) )],
    #         y=hodld,
    #         name="sats held"
    #     ))
    # # fig.add_trace(
    #     go.Scatter(
    #         x=[*range( len(res[KEY_ESTIMATED_NETWORK_HASHRATE]) )],
    #         # this magic just takes each element and divides..
    #         # so the units are now exahash and the numbers on the graph are such the more prettier...mmm ok?
    #         y=[e / MEGAHASH for e in res[KEY_ESTIMATED_NETWORK_HASHRATE]],
    #         name="network hashrate"
    #     ))

    # Set x-axis title
    fig.update_xaxes(title_text="time (months)")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>satoshi</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Bitcoin price</b>", secondary_y=True)

    fig.update_layout(barmode='stack')
    html = fig.to_html(include_plotlyjs="require", full_html=False)

    #logging.debug(html)

    return html

###################################
def make_table_string(res) -> str:
    str_table = \
"""| month | block height | network exahash | btc price |
| :--- | ---: | ---: | ---: |
"""
    # 1         2      3      4

                            #    1    2    3    4 
    str_table_row_format = """| %s | %s | %s | %s |"""

    for mdx in range(len(res[KEY_ESTIMATED_HEIGHT])):
        str_table += str_table_row_format % ( \
            f"{mdx + 1}",
            f"{res[KEY_ESTIMATED_HEIGHT][mdx]:,}",
            f"{res[KEY_ESTIMATED_NETWORK_HASHRATE][mdx]/MEGAHASH:,.2f}",
            f"{res[KEY_ESTIMATED_PRICE][mdx]:,.2f}"
        )
        str_table += '\n'

    # TODO - THE STORY
    # story = "Your strategy is to " + pin.pin['strategy'] + ".  "
    # story += "This means, once you have earned " + str(selling_threshold) + " sats, your can withdrawal them from your mining pool and sell or hold on to them.  "

    # total = str(int(_cost_electricity[0] + _cost_operating[0]))

    # if pin.pin['strategy'] == USER_STRATEGY_1:
    #     story += "You've decided to sell only enough sats to cover the $" +  total + " monthly expenses you have."

    # if pin.pin['strategy'] == USER_STRATEGY_2:
    #     story += "You've decided to not sell your bitcoin.  You are going to HODL.  So when it comes to the monthly expense... how will you pay your monthly bills of $" + total + "?..."  

    # if pin.pin['strategy'] == USER_STRATEGY_3:
    #     story += "You've decided to sell ALL the bitcoin you withdrawal and roll in stead money coming your way."

    return str_table
