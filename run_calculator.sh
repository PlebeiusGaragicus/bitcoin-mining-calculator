# activate the python virtual environment
# same as typing "source ./venv/bin/activate" when in the terminal
. ./venv/bin/activate

# look for Luxor API key
if [ -f ./apikey ]; then
    apikey="$(cat ./apikey)"
    echo using Luxor API key - $apikey
    # run the calculator script with supplied key
    python3 ./src/main.py --key=$apikey "$@"
    # OR THIS... same same
    #python3 ./src/main.py --key=ha83lahfoobar3ial3ialf8 "$@"
else
    echo "Luxor api key file '#PWD/apikey' not found"
    python3 ./src/main.py $@
fi
