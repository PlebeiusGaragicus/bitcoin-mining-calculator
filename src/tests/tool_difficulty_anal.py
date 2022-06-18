# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

import logging
import json
import urllib.request as ur

from pywebio import pin
from pywebio import output

from constants import *

def get_difficulty(bits: int):
    """
        This converts the 'bits' field in a bitcoin block to the 'difficulty' number

        Taken (AKA, shamelessly plagiarized) from bitcoin core:
            https://github.com/bitcoin/bitcoin/blob/8f3ab9a1b12a967cd9827675e9fce112e51d42d8/src/rpc/blockchain.cpp#L75-L95
        Also helpful:
            https://en.bitcoin.it/wiki/Difficulty
            https://stackoverflow.com/a/22161019
            https://bitcoin.stackexchange.com/questions/30467/what-are-the-equations-to-convert-between-bits-and-difficulty
            https://bitcointalk.org/index.php?topic=192886.0

        ...or just use this shell script     ¯\_(ツ)_/¯
        #!/bin/bash
        echo "ibase=16;FFFF0000000000000000000000000000000000000000000000000000 / $1" | bc -l
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
