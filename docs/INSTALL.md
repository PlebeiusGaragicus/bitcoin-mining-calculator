# INSTALL BITCOIN

### FIRST TIME INSTALL - CONFIGURE
Only if this is your first time running thru this on your system!!!
```sh
# install xcode tools
xcode-select --install
# Install brew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install automake libtool boost pkg-config libevent
```

## FRESH INSTALL - BITCOIN (MacOS)
```sh
cd ~/Desktop
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin
./autogen.sh
./configure --without-wallet --with-gui=no
make
```

### run bitcoind
```sh
./src/bitcoind
```

# INSTALL THIS CALCULATOR
```sh
cd ~/Desktop
git clone https://github.com/PlebeiusGaragicus/bitcoin-mining-calculator.git
cd bitcoin-mining-calculator
python3 -m venv venv/
source venv/bin/activate
/Users/PlebeiusG/Desktop/bitcoin-mining-calculator/venv/bin/python3 -m pip install --upgrade pip
pip install -r requirements.txt
./run_calculator.sh —debug
```

## run 
```sh
./run_calculator.sh
```

## run - with a bitcoin node on the same network
```sh
./run_calculator.sh --rpcip=<YOUR.UP.RIGHT.HERE:8332> --rpcuser=<USERNAME:PASSWORD>
```

#### run demo
```sh
# run bitcoind
/Users/PlebeiusG/Desktop/bitcoin/src/bitcoind -datadir="/Volumes/core-mobile/bitcoin"
/Users/PlebeiusG/Desktop/bitcoin-mining-calculator/run_calculator.sh --debug
```
