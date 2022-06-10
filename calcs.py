# DO THE CALCULATIONS

import logging

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from constants import *


# TODO find source code in bitcoin
def block_subsity( height ):
    return (50 * ONE_HUNDRED_MILLION) >> (height // SUBSIDY_HALVING_INTERVAL)

# TODO find source code in bitcoin - (is this even in the code?)
def blocks_until_halvening(block_height):
    return ((block_height // SUBSIDY_HALVING_INTERVAL + 1) * SUBSIDY_HALVING_INTERVAL) - block_height


def usd(sats, price):
    return sats * (price / ONE_HUNDRED_MILLION)

def btc(dollars, price):
    return int(ONE_HUNDRED_MILLION * (dollars / price))



##########################
 # TODO - FUTURE GENERALIZATION IMPROVEMENT@@@!!! , miner_list, network_stats):
def calculate_projection(months, height, avgfee, hashrate, wattage, price, pricegrow, pricegrow2, pricelag, networh_hashrate, hashgrow, kWh_rate, opex, capex, resale_upper, resale_lower, poolfee):
    res = {
        # THESE ARE THE INPUTS TO THE CALCULATION
        KEY_MONTHS_TO_PROJECT : months,
        # TODO _ USE THIS FOR BACKWARDS MODEL TESTING
        KEY_START_HEIGHT : height,
        KEY_AVGFEE : avgfee,
        KEY_MY_HASHRATE : hashrate,
        KEY_WATTAGE : wattage,
        KEY_START_PRICE : price,
        KEY_PRICE_GROWTH : pricegrow,
        KEY_PRICE_GROWTH2 : pricegrow2,
        KEY_PRICE_LAG : pricelag,
        KEY_START_NH : networh_hashrate,
        KEY_HASH_GROWTH : hashgrow,
        #KEY_HASH_GROWTH2 : hashgrow2,
        KEY_MONTHLY_OPEX : opex,
        KEY_CAPEX : capex, # sats
        KEY_RESALE_UPPER : resale_upper,
        KEY_RESALE_LOWER : resale_lower,
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

    # TODO VARIABLES TO ADD\
    # start price
    # avg blk sub


    # TODO - the 
    dollar_capex = usd(capex, price=price)

    # have we crossed a halvening?  We use this to determine which growth factor to use with price/nh
    crossed = False
    # this used in conjunction with pricelag
    month_we_crossed = 0

    for m in range(months):
        hashvalue = 0
        poolfee = 0
        _kwh = 0

        # DO ONE DAY OF CALCULATIONS
        for _ in range(30):

            if blocks_until_halvening( height ) < EXPECTED_BLOCKS_PER_DAY:
                logging.debug(f"we will cross a halvening, block: {height}")
                crossed = True
                month_we_crossed = m

                # GO BLOCK BY BLOCK
                for _ in range( EXPECTED_BLOCKS_PER_DAY ):

                    #hashvalue += us.total_terahash() * (block_subsity( _blk ) + ns.fee_average) * (1 - user_pool_fee()) / _nh
                    hashvalue += hashrate * (block_subsity( height ) + avgfee) * (1 - poolfee) / networh_hashrate
                    #_kwh += us.total_wattage() / 6000 / us.total_terahash()
                    _kwh += wattage / 6000

                    height += 1

            # DO A WHOLE DAY AT A TIME
            else:
                logging.debug(f"we will NOT cross a halvening - calculating one day : at block {height} until: {blocks_until_halvening(height)}")

                hashvalue += hashrate * (block_subsity( height ) + avgfee) * (1 - poolfee) * EXPECTED_BLOCKS_PER_DAY / networh_hashrate
                #hashvalue += (block_subsity( _blk ) + ns.fee_average) * (1 - user_pool_fee()) * EXPECTED_BLOCKS_PER_DAY / _nh
                #_kwh += 24 * us.total_wattage() / 1000 / us.total_terahash()
                _kwh += 24 * wattage / 1000

                height += EXPECTED_BLOCKS_PER_DAY

            # END OF DAY STUFF
            networh_hashrate *= 1 + hashgrow / 30

        # END OF MONTH STUFF - now we have to settle


        # if we have crossed the halvening AND it's been 'LAG MONTHS' since... use pricegrow2
        if crossed and m - month_we_crossed >= pricelag:
            price *= 1 + pricegrow2
            logging.debug(f"price increased to {price} - using growth factor2: {pricegrow2}")
        else:
            # if we haven't crossed a halvening... OR it hasn't been 'LAG MONTHS' yet
            price *= 1 + pricegrow # 1 + pricegrow / 30 # daily
            logging.debug(f"price increased to {price} - using growth factor2: {pricegrow2}")

        # TODO
        # if no profit
            # unplug
        # if duck, fuck, squeeze... log it!

        sold_e = btc(_kwh * kWh_rate, price=price)
        sold_o = btc(opex, price=price) # we divide opex by my hashrate because everything else on this graph is reduced in this manner
        
        # ARE WE JUST GOING TO FACTOR IN THE RESALE JUST LIKE THAT, HUH?  OK...
        # TODO .. MAKE A NEW ONE CALLED RE-SALE RECAPTURE... AND IT LOWERS?  IS IT NEGATIVE?
        #sold_c = resale_percent * capex / months #already in 
        sold_c = capex / months #already in btc terms
        #sold_c = capex / months #already in btc terms

        breakeven_price = ((ONE_HUNDRED_MILLION * opex) + (ONE_HUNDRED_MILLION * _kwh * kWh_rate)) / (hashvalue - sold_c)

        # duck fuck squeeze
        # if sold_e + sold_o + sold_c > hashvalue:
        #     hashvalue = 0
        #     sold_e = 0
        #     sold_o = 0
        #     sold_c = 0

        res[KEY_ESTIMATED_HEIGHT].append( height )
        res[KEY_ESTIMATED_NETWORK_HASHRATE].append( networh_hashrate )
        res[KEY_ESTIMATED_PRICE].append( price )
        #res[KEY_ESTIMATED_AVGFEE].append( 0 )

        res[KEY_HASHVALUE].append( hashvalue )
        res[KEY_KWH].append( _kwh )

        res[KEY_SOLD_ELECTRICITY].append( sold_e )
        res[KEY_SOLD_OPEX].append( sold_o )
        res[KEY_SOLD_CAPEX].append( sold_c )

        # basically, just the decision/assumption-making/verifying helper variables
        #beprice = hashvalue * ((_kwh * cost_kWh) + (sold_c) + (opex / us.total_terahash())) / ONE_HUNDRED_MILLION
        #beprice = ((_kwh * cost_kWh) + (dollar_capex) + (opex / us.total_terahash())) / hashvalue * ONE_HUNDRED_MILLION

        res[KEY_BREAKEVEN_PRICE].append( breakeven_price )
        # KEY_BREAKEVEN_PRICE_P20P : [],
        # KEY_BREAKEVEN_NH : [],


    return res







##########################
def pretty_graph(res):
    """
        this takes the projection results and returns a pretty graph
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
    fig.update_xaxes(title_text="xaxis title")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>satoshi</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Bitcoin price</b>", secondary_y=True)

    fig.update_layout(barmode='stack')
    return fig.to_html(include_plotlyjs="require", full_html=False)




##########################
def make_table_string(res) -> str:
    #verbose = bool(pin.pin['verbose'])
    #log it ("verbose:", verbose)


    # https://docs.python.org/3/library/string.html
# 1       2              3                             4
    str_table = """
| month | block height | network hashrate (exahash) | btc price |
| :--- | ---: | ---: | ---: |
"""
# 1       2      3      4   

                            #    1    2    3    4 
    str_table_row_format = """| %s | %s | %s | %s |"""

    for mdx in range(len(res[KEY_ESTIMATED_HEIGHT])):
        str_table += str_table_row_format % ( \
            f"{mdx + 1}",
            f"{res[KEY_ESTIMATED_HEIGHT][mdx]:,}",
            f"{res[KEY_ESTIMATED_NETWORK_HASHRATE][mdx]/MEGAHASH:,.2f}",
            f"{res[KEY_ESTIMATED_PRICE][mdx]:,.2f}",
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

