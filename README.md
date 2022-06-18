# the open-source bitcoin mining profitability calculator

This tool helps you decide when/if to invest in bitcoin mining equipment

```
"All models are wrong, but some models are useful." 
    -statistician George Box
```

This tool is for prospective bitcoin miners to understand the economics involved in bitcoin mining and to help aid in purchase decisions of bitcoin mining hardware - you can use it to calculate the potential earnings/costs of running any bitcoin mining equipment.  This project aims to be an open-source example of - and alternative to - bitcoin mining profitability calculators found online today (in 2022).  I hope to explain big concepts as I go and provide comments/documentation where possible to enable everyone's understanding of this technology.

This repository should revolve around teaching the ideas behind bitcoin mining and to encourage the smart, expansion of bitcoin mining - even at home.

The included code aims to be as easy to use as possible; with or without running your own Bitcoin archive node.

I am a pleb ```¯\_(ツ)_/¯``` whose goal it is to inspire the next generation of coders to develop open-source tools for the world and, above all, to remind you that you don't have to be an expert in order to participate in this global bitcoin network.

# How to install
```sh
git clone https://github.com/PlebeiusGaragicus/bitcoin-mining-calculator.git
cd bitcoin-mining-calculator

python3 -m venv venv/
source venv/bin/activate

python3 -m pip install --upgrade pip
pip install -r requirements.txt

chmod +x ./run_calculator.sh
```

# How to run
```sh
./run_calculator.sh
```

# How to use
This project is meant to be run on a system with a local bitcoin node running, namely, bitcoin core.  If it finds ```bitcoin-cli``` on the system and successfully runs the ```getblockchaininfo``` command to find a fully synced node, it will pull needed data from that (network difficulty and block height).  If unable to pull from a local node, it will use https://blockchain.info's API.  It also pulls price data from either Luxor's API (https://github.com/LuxorLabs/hashrateindex-api-python-client) if you have an API key, or Coinbase's API (https://api.coinbase.com).

# Additional Features
This project also includes a feature to analyse the history of both bitcoin price and difficulty/hashrate over time.  These features need an API key from Luxor - see: https://github.com/LuxorLabs/hashrateindex-api-python-client

To enable, put your Luxor API key in a file called apikey.py in the format
```python
LUXOR_API_KEY = "<YOUR KEY HERE IN QUOTES>"
```

This project also includes a feature to analyze the history of block fees but requires a local bitcoin core node to pull this data from.

This project also includes a fiat <-> bitcoin currency converter.

# How to Contribute

Send me a pull request!

I'm new to github and collaborating, but I'll figure it out!



# I stand on the shoulders of giants...

See also:
- https://github.com/bitcoinbook/bitcoinbook
- https://insights.braiins.com/en/profitability-calculator/
- https://www.aniccaresearch.tech/blog/the-intelligent-bitcoin-miner-part-i
- https://data.hashrateindex.com/network-data/btc
