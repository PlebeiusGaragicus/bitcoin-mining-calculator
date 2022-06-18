# activate the python virtual environment
. ./venv/bin/activate

# look for Luxor API key
if [ -f ./apikey ]; then
    apikey="$(cat ./apikey)"
    #echo using Luxor API key - $apikey
    echo using Luxor api key file
    # run the calculator script with supplied key
    python3 ./src/btc-mining-calcs/main.py -k $apikey "$@"
    # OR THIS... same same
    #python3 ./src/main.py --key=$apikey "$@"
else
    # run the calculator script
    echo Luxor api key file not found
    python3 ./src/btc-mining-calcs/main.py $1
fi
