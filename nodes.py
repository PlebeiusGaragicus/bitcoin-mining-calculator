# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
Bro, do you even run a bitcoin node?
If so, this module helps pull sweet, sweet datums from it.
Mmmm, datums... :()
"""

import logging

import os
import json

from pywebio import output
from pywebio import pin

from constants import *

def useful_node():
    """
        returns path to bitcoin-cli if node is (1) found, (2) running, (3) up-to-date - not in IDB
        returns None on error
    """

    bin_path = os.popen("which bitcoin-core.cli").read().strip('\n')
    if bin_path == '':
        bin_path = os.popen("which bitcoin-cli").read().strip('\n')
        if bin_path == '':
            logging.info("Could not find bitcoin core on this machine")
            return None

    logging.info(f"bitcoin core found at: {bin_path}")

    try:
        # https://developer.bitcoin.org/reference/rpc/getblockchaininfo.html
        node_info = json.loads( os.popen(f"{bin_path} getblockchaininfo 2> /dev/null").read() ) # stderr is thrown away...
        #node_info = json.loads( os.popen(f"{bin_path} getblockchaininfo").read() )

        ibd = bool( node_info['initialblockdownload'] )
        logging.info(f"Node in Initial Block Download? {ibd}")
        progress = float( node_info['verificationprogress'] )
    except Exception as e:
        logging.warning("Your bitcoin node does not appear to be running.")
        return None

    logging.info(node_info)

    if ibd == True:
        logging.error(f"ERROR: your node is currently downloading the blockchain, it is not fully sync'd yet ({float(progress * 100):.0f}% downloaded)")
        return None

    logging.info(f"This node appears up-to-date - we can use it!")

    return bin_path


def node_blockheight(bcli_path) -> int:
    """
    this will run bitcoin-cli at the supplied path
    TODO - provide link to bitcoin documentatiopn of 'getblockcount'
    """
    return int(os.popen(f"{bcli_path} getblockcount").read())


def node_blockhash(bcli_path, height) -> int:
    """
        TODO - I need a link to bitcoin documentation here
    """
    return os.popen(f"{bcli_path} getblockhash {height}").read()


def node_networkhashps(bcli_path, nblocks=120, height=-1) -> float: # use -1 for nblocks to go since last diff change
    """
    """
    # https://developer.bitcoin.org/reference/rpc/getnetworkhashps.html
    nh = os.popen(f"{bcli_path} getnetworkhashps {nblocks} {height}").read()
    return float( nh.split('\n')[0] ) / TERAHASH





##########################################################################
def node_avgblockfee(bcli_path, nBlocks = EXPECTED_BLOCKS_PER_DAY) -> int:
    """
    """
    blockheight = int(os.popen(f"{bcli_path} getblockcount").read())

    with output.popup(f"Averaging transactions fees for last {nBlocks} blocks...", closable=False) as p:

        pin.put_input("remaining", value=nBlocks, label="Blocks remaining:")
        pin.put_textarea("feescroller", value='')
        pin.put_input('sofar', value='', label="Average so far:")
        output.put_button("Stop early", color='danger', onclick=lambda: output.close_popup())

        total_fee = 0
        for bdx in range(blockheight-nBlocks, blockheight):
            block_fee = int( os.popen(f"""{bcli_path} getblockstats {bdx} '["totalfee"]'""").read().split(': ')[1].split('\n')[0] )        
            total_fee += block_fee
            pin.pin['remaining'] = blockheight - bdx
            pin.pin['sofar'] = f"{ (total_fee / (1 + bdx - blockheight + nBlocks)) :,.2f}"

            try:
                pin.pin['feescroller'] = f"block: {bdx} --> fee: {block_fee:,}\n" + pin.pin["feescroller"]
            except Exception as e:
                logging.debug("", exc_info=True)
                # this error happens if the popup was closed
                return round(total_fee / (1 + bdx - blockheight + nBlocks), 2)
            logging.info(f"block: {bdx} -->  fee: {format(block_fee, ',').rjust(11)} satoshi")

    output.close_popup()

    total_fee /= nBlocks

    logging.info(f"average block fee over last {nBlocks} blocks is {total_fee:,.2f} satoshi")
    return round(total_fee, 2)
