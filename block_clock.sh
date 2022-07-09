cat block_clock.sh 
# if you run this script on macos...
# - install homebrew
# - run these:
#   - brew install jq
#   - brew install coreutils

clear

path=$(which bitcoin-core.cli)

if [ -z "$path" ]
then
path=$(which bitcoin-cli)
fi

if [ -z "$path" ]
then
    echo "bitcoin core not installed... using blockchain.info"
    alias blockheight="python3 -c \"import urllib.request as ur;print(int(ur.urlopen(ur.Request('https://blockchain.info/q/getblockcount')).read()))\""

    blockhash() {
        echo $(python3 -c "import urllib.request as ur;print(str(ur.urlopen(ur.Request('https://blockchain.info/block-height/$1?format=json')).read(),'utf-8'))") | jq -r '.blocks[0].hash'
    }

    fee() {
        h=$(blockhash $1)
        f=$(echo $(python3 -c "import urllib.request as ur;print(str(ur.urlopen(ur.Request('https://blockchain.info/rawblock/$h')).read(),'utf-8'))") | jq -r '.fee')
        echo $(numfmt --grouping $f)
    }

    nh() {
        echo "-1"
    }

    sleeptime=20

else
    echo "bitcoin core found at $path"
    alias blockheight="$path getblockcount"
    alias blockhash="$path getblockhash"

    fee() {
        echo $(numfmt --grouping $($path getblockstats $1 '["totalfee"]' | jq -r '.totalfee'))
    }

    nh() {
        echo $($path getnetworkhashps)
    }

    sleeptime=2
fi

show() {
    echo "time="$(date +%s)"  height="$1"  hash="$(blockhash $1)"  nh="$(nh)"  fee="$(fee $1)
}

seconds() {
    echo $(echo $(date +%s)-$last_sec | bc) seconds later
}

prev=$(blockheight)
#prev=$(echo $(blockheight) - 1| bc) #DEBUG
last_sec=$(date +%s)

show $prev
while true;do
    cur=$(blockheight)

    if [ "$cur" != "$prev" ]; then
        echo
        seconds
        last_sec=$(date +%s)
        show $cur
        prev=$cur
    fi

    /bin/sleep $sleeptime
    echo '.\c'
done