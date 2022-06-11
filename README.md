# bitcoin-mining-calculator
This tools helps you decide when to invest in bitcoin mining equipment

# INSTALL
```sh
git clone https://github.com/PlebeiusGaragicus/bitcoin-mining-calculator.git
cd bitcoin-mining-calculator

python3 -m venv venv/
source venv/bin/activate

python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

# Goals and Intent
- To calculate the potential earnings of any bitcoin miner
- To be an open-source example of - and alternative to - bitcoin mining profitability calculators found online today (in 2022)
- To teach the incentives behind bitcoin mining and to encourage at-home bitcoin mining
- To be an as-easy-to-use-as-possible script you can run on your own computer (with or without running your own Bitcoin archive node)
- To explain big concepts as I go and provide comments/documentation where possible to enable everyone's understanding of this technology
- To inspire the next generation of coders to develop open source tools for bitcoin and the world
- To remind you that you don't have to be an expert in order to participate in this global human network
- To spread the love and the bitcoin

# I stand on the shoulders of giants...

- https://insights.braiins.com/en/profitability-calculator/
- https://github.com/LuxorLabs

# TODO

- uhhh.. make sure it works.  The projection/graph is not accurate
- make the graph pretty-er
- change startup 'init' ... don't make it count fees at startup... have the user do it later
- add miner break-even analyzis popup
- block fee analysis popup
- price history analysis popup
- network hashrate analysis popup, moving average, future projection, etc etc etc...
- CSV file download of projection table
- put more datums in the table... TABLE DATUMMMMSSS.... <3
- Integrate spruned repo (one click install, catch and diagnose all errors - be easy to use)
- +/- 5% TH on the miner?