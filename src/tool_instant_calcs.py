# INSPIRED BY: https://insights.braiins.com/en

#################################
# ADJUST YOUR SETTINGS HERE!!
#################################
watts = 3050
th = 90
pool_fee = 0
cost_kWh = 0.04

if __name__ == "__main__":
    import urllib.request as ur
    def p(label, what):
        print(f"{label:20} --> {repr(what).ljust(20)}")

    kilohash = 1000
    megahash = 1000000
    gigahash = 1000000000
    terahash = 1000000000000
    petahash = 1000000000000000
    exahash  = 1000000000000000000
    one_hundred_million = 100000000
    expected_blocks_per_day = 24 * 6 #144
    # https://github.com/bitcoin/bitcoin/blob/master/src/validation.cpp
    halves_every = 210000 #blocks
    print("------------------------------------------------")
    print("All models are wrong,")
    print("                     but some models are useful")
    print()
    print("...edit this file to adjust wattage/hashrate...")
    print()
    print()

    #################################
    # NETWORK HASHRATE
    #################################
    # https://www.blockchain.com/api/blockchain_api
    # https://jsapi.apiary.io/apis/blockchaininfo/reference/simple-real-time-data/total-bitcoin/get.html
    difficulty = int(float(ur.urlopen(ur.Request('https://blockchain.info/q/getdifficulty')).read()))
    hashrate_calc = difficulty * (2**32) / 600 / terahash
    hashrate_est = int(ur.urlopen(ur.Request('https://blockchain.info/q/hashrate')).read()) / 1000
    nth = (hashrate_calc + hashrate_est) / 2

    p("network difficulty", difficulty)
    p("hashrate calculated", int(hashrate_calc))
    p("hashrate estimate", int(hashrate_est))
    p("using hashrate of", int(nth))
    print()

    #################################
    # BLOCK REWARD
    #################################
    block_height = int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read())
    next_halvening = ((block_height // halves_every + 1) * halves_every) - block_height

    block_reward = 50 * one_hundred_million
    block_reward >>= block_height // halves_every

    fee_average = 0 * one_hundred_million
    reward = block_reward + fee_average

    p("block height", block_height)
    p("next halvening", next_halvening)
    p("block reward", block_reward)
    p("average fees", fee_average)
    p("total reward", reward)
    print()

    #################################
    # PRICE
    #################################
    price_bitcoin =  int(float(ur.urlopen(ur.Request('https://blockchain.info/q/24hrprice')).read()))
    price_satoshi = price_bitcoin / one_hundred_million

    p("bitcoin price $", price_bitcoin)
    p("price of one sat $", price_satoshi)
    print()

    #################################
    # MY HASHRATE
    #################################
    eff = watts / th
    #mth = watts / eff

    p("wattage", watts)
    p("efficiency (W/Th)", eff)
    #p("my hashrate", mth)
    p("my hashrate", th)
    print()

    #################################
    # REWARD
    #################################
    #share = mth / nth
    share = th / nth
    rawreward = share * reward
    s10 = rawreward * (1 - pool_fee)
    value = s10 * price_satoshi

    p("share of hashrate", share)
    p("reward sats / block", rawreward)
    p("pool fee %", pool_fee)
    p("sats to pool", pool_fee * rawreward)
    p("sats to me", s10)
    print()

    #################################
    # ENERGY BURNED
    #################################
    kWh = watts / 6000
    cost = cost_kWh * kWh

    p("$ per kWh", cost_kWh)
    p("kWh burned / block", kWh)
    print()

    #################################
    # COST / VALUE
    #################################
    daily_value = value * expected_blocks_per_day
    daily_cost = cost * expected_blocks_per_day


    p("INCOME / block $", value)
    p("COST / block $", cost)
    print()

    #################################
    # DISCOUNT
    #################################
    ppps = int(cost / s10 * one_hundred_million) #price paid per satoshi

    discount = int((1 - (ppps / price_bitcoin)) * 100)

    #p("$ / sat earned:", pps)
    #p("$ / sat bought:", price_bitcoin)
    p("price btc MINED:", ppps)
    p("price btc BOUGHT:", price_bitcoin)
    p("discount %", discount)
    print()

    #################################
    # DAILY
    #################################
    p("daily expense $", daily_cost)
    p("daily income $", daily_value)
    print()
    if value > cost:
        print("Profit - you are getting bitcoin at a discount!")
    else:
        print("Loss - you are paying a premium for bitcoin.  Turn off your miner if you don't need the heat.")
    print()
