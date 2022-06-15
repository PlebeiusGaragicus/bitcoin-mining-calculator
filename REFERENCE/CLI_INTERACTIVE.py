# All models are wrong, but some models are useful

import urllib.request as ur

def average_fees(nBlocksToAverage) -> int:
    return 111 * nBlocksToAverage

ONE_HUNDRED_MILLION = 100_000_000
EXPECTED_BLOCKS_PER_DAY = 24 * 6 #144
HALVES_EVERY = 210_000 #blocks

price_bitcoin =  int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))
block_height = int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read())

next_halvening = ((block_height // HALVES_EVERY + 1) * HALVES_EVERY) - block_height
block_reward = 50 * ONE_HUNDRED_MILLION
block_reward >>= block_height // HALVES_EVERY

fee_average = average_fees( EXPECTED_BLOCKS_PER_DAY )

reward = block_reward + fee_average

nh = int(ur.urlopen(ur.Request('https://blockchain.info/q/hashrate')).read()) / 1000

watts = float(input("Your wattage : ")) # TODO - I wrote an input function just for this
mh = float(input("Your tera-hashrate : ")) # TODO - I wrote an input function just for this

share = mh / nh
rawreward = share * reward

cost_kWh = float(input("Cost per kilo-watthour ($): "))

kWh = watts / 6000
cost = cost_kWh * kWh

pool_fee = float(input("Pool fee (%): "))

s10 = rawreward * (1 - pool_fee)
value = s10 * price_bitcoin / ONE_HUNDRED_MILLION

daily_value = value * EXPECTED_BLOCKS_PER_DAY
daily_cost = cost * EXPECTED_BLOCKS_PER_DAY

ppps = int(cost / s10 * ONE_HUNDRED_MILLION) #price paid per satoshi

discount = int((1 - (ppps / price_bitcoin)) * 100)
