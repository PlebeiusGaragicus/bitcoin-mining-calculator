# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

"""
Bro, do you even run a bitcoin node?
If so, this module helps pull sweet, sweet datums from it.
Mmmm, datums... <(O.o)>
"""

from inspect import getblock
import os
import logging
import json

from pywebio import output
from pywebio import pin

from constants import *
import config
from calcs import get_hashrate_from_difficulty

###########################
def verify_node() -> bool:

    if config.RPC_enabled:
        if verify_RPC_node():
            return True
        else:
            logging.error("RPC is enabled but the node is not valid")
            return False

    if verify_local_node():
        return True
    else:
        logging.error("local node found is not valid")
        return False

##############################
def find_local_node() -> str:
    """
        searches for bitcoin-cli or bitcoin-core.cli on local system

        returns string as path to executable
        returns None if unable to find
    """
    bin_path = os.popen("which bitcoin-core.cli").read().strip('\n')
    if bin_path == '':
        bin_path = os.popen("which bitcoin-cli").read().strip('\n')
        if bin_path == '':
            logging.info("Could not find bitcoin core on this machine")
            return None

    logging.info(f"bitcoin core found at: {bin_path}")
    
    return bin_path

###################
def verify_local_node() -> str:
    """
        returns path to bitcoin-cli if node is (1) found, (2) running, (3) up-to-date - not in IDB
        returns None on error
    """

    bin_path = find_local_node()

    try:
        # https://developer.bitcoin.org/reference/rpc/getblockchaininfo.html
        #node_info = json.loads( os.popen(f"{bin_path} --rpcuser=__cookie__ --rpcpassword={config.cookie} getblockchaininfo 2> /dev/null").read() ) # stderr is thrown away...
        #resp = os.popen(f"{bin_path} --rpcuser=__cookie__ --rpcpassword={config.cookie} getblockchaininfo 2> /dev/null").read()
        resp = os.popen(f"{bin_path} getblockchaininfo 2> /dev/null").read()
        node_info = json.loads( resp ) # stderr is thrown away...
        #node_info = json.loads( os.popen(f"{bin_path} getblockchaininfo").read() )
        logging.info(f"getblockchaininfo: {node_info}")

        ibd = bool( node_info['initialblockdownload'] )
        logging.info(f"Node in Initial Block Download? {ibd}")

        pruned = bool( node_info['pruned'] )
        config.pruned = pruned
        logging.info(f"Node is pruned? {pruned=}")

        if pruned:
            config.pruned_height = int(node_info['pruneheight'])
            logging.info(f"Node is pruned to block: {config.pruned_height}")

        progress = float( node_info['verificationprogress'] )
    except json.decoder.JSONDecodeError:
        #logging.exception("Error running `getblockchaininfo`")
        logging.error("Your bitcoin node does not appear to be running.")
        return None

    if ibd == True:
        logging.error(f"ERROR: your node is currently downloading the blockchain, it is not fully synced yet ({float(progress * 100):.0f}% downloaded)")
        return None

    logging.info(f"This node appears up-to-date - we can use it!")
    return bin_path

#######################################
def get_stats_from_node() -> bool:
    """
        This function updates the 'pin' input fields (height, network difficulty and hashrate) by pulling
            data from the supplied bitcoin-cli

        Returns True if successful, False on error
    """
    if not verify_node():
        return False

    try:
        h = getblockcount()
        config.height = h

        diff = getdifficulty()
        config.difficulty = diff

        nh = round(get_hashrate_from_difficulty(diff), 2)
        #nh = round((d * 2 ** 32) / 600 / TERAHASH, 2)
        #nh = node_networkhashps(path)
        #f = node_avgblockfee(path)

        pin.pin[PIN_HEIGHT] = h
        pin.pin[PIN_NETWORKDIFFICULTY] = diff
        #pin.pin[PIN_NETWORKHASHRATE] = f"{nh:,} TH/s"
        #pin.pin_update(PIN_NETWORKHASHRATE, help_text=f"{nh/MEGAHASH:.2f} EH/s")
        #pin.pin_update(name=PIN_AVERAGEFEE, help_text=f"= {f / ONE_HUNDRED_MILLION:.2f} bitcoin")
    except Exception:
        logging.exception(f'__func__')
        return False

    return True

##########################################################
def run_RPC_command(command: str, params=None) -> str:
    """
        note: run this in a try/except block becuase it may raise exception (json.decoder.JSONDecodeError)
    """
    if not config.RPC_enabled:
        raise Exception(f"RPC is not enabled but get_RPC_command was called")

    logging.debug(f"run_RPC_command({command}, {params})")

    if params == None:
        cmd = "curl -s --user {} -X POST http://{} --data-binary '{{\"jsonrpc\":\"1.0\",\"id\":\"miningcalcs<3\",\"method\":\"{}\"}}' -H 'Content-Type: application/json'".format(config.RPC_user_pass, config.RPC_ip_port, command, params)
    else:
        if type(params) == str:
            cmd = "curl -s --user {} -X POST http://{} --data-binary '{{\"jsonrpc\":\"1.0\",\"id\":\"miningcalcs<3\",\"method\":\"{}\", \"params\": [ \"'{}'\" ]}}' -H 'Content-Type: application/json'".format(config.RPC_user_pass, config.RPC_ip_port, command, params)
        else:
            cmd = "curl -s --user {} -X POST http://{} --data-binary '{{\"jsonrpc\":\"1.0\",\"id\":\"miningcalcs<3\",\"method\":\"{}\", \"params\": [ '{}' ]}}' -H 'Content-Type: application/json'".format(config.RPC_user_pass, config.RPC_ip_port, command, params)

    logging.debug(f"{cmd}")
    result = json.loads( os.popen(cmd).read() )

    logging.debug(f"got this: {result}") #TODO FIX THIS... actually returns ['result]
    result = result['result']
    logging.debug(f"returning: {result}") #TODO FIX THIS... actually returns ['result]
    return result

###############################
def verify_RPC_node() -> bool:
    """
        TODO
    """
    # if not config.RPC_enabled:
    #     raise Exception("WHAT THE FUCK YOU SHOULN'D HAVE CALLED THIS")
    #cmd = get_RPC_command('getblockchaininfo')

    try:
        node_info = run_RPC_command('getblockchaininfo')
        # TODO add "2> /dev/null"
        #node_info = json.loads( os.popen(cmd).read() )['result']
        logging.info(f"getblockchaininfo: {node_info}")

        ibd = bool( node_info['initialblockdownload'] )
        logging.info(f"Node in Initial Block Download? {ibd}")

        pruned = bool( node_info["pruned"] )
        config.pruned = pruned
        logging.info(f"Node info: {pruned=}")

        if pruned:
            config.pruned_height = int(node_info['pruneheight'])
            logging.info(f"Node is pruned to block: {config.pruned_height}")
    except json.decoder.JSONDecodeError:
        logging.error("Your bitcoin node does not appear to be running.")
        return False

    if ibd:
        progress = float( node_info['verificationprogress'] )
        logging.error(f"ERROR: your node is currently downloading the blockchain, it is not fully synced yet ({float(progress * 100):.0f}% downloaded)")
        return None

    logging.info(f"This node appears up-to-date - we can use it!")
    return True

########################################
def getblockcount() -> int:
    """
        basically just runs the 'getblockcount' command
        https://developer.bitcoin.org/reference/rpc/getblockcount.html
    """
    if config.RPC_enabled:
        return run_RPC_command('getblockcount')

    if config.node_path != None:
        return int(os.popen(f"{config.node_path} getblockcount").read())

    raise Exception("getblockcount() called but no node is setup")

########################################
def get_block_unix_time(height) -> int:
    """
        This returns a string with the formatted date of a block at a given height
        https://developer.bitcoin.org/reference/rpc/getblockstats.html
    """
    try:
        if config.RPC_enabled:
            ret = run_RPC_command('getblockstats', height) # we aren't going to give it the 'time' parameter becuase that's more shit to code... so just parse it out here
            return int(ret['time'])

        if config.node_path != None:
            ret = os.popen(f"{config.node_path} getblockstats {height} '[\"time\"]'").read()
            return int(json.loads(ret)["time"])

    except json.decoder.JSONDecodeError:
        # this will fail if the node is unable to return the block time (eg. pruned node)
        logging.debug("json decode error - are you running a pruned node?")
        return None

    raise Exception("get_block_unix_time() called but no node is setup")

##############################################
def getblockhash(height) -> str:
    """
        basically just runs the 'getblockhash' command
        https://developer.bitcoin.org/reference/rpc/getblockhash.html
    """
    logging.debug(f"getblockhash({height})")

    if config.RPC_enabled:
        ret = run_RPC_command('getblockhash', height)
        return ret

    if config.node_path != None:
        return os.popen(f"{config.node_path} getblockhash {height}").read()

    raise Exception("get_block_unix_time() called but no node is setup")
    # return None ??? instead of throwing an error?

# # TODO - use -1 for nblocks to go since last diff change
# ####################################################################
# def getnetworkhashps(nblocks=120, height=-1) -> float:
#     """
#         basically just runs the 'getnetworkhashps' command
#         https://developer.bitcoin.org/reference/rpc/getnetworkhashps.html
#     """
#     if config.node_path == None:
#         return None

#     nh = os.popen(f"{config.node_path} getnetworkhashps {nblocks} {height}").read()

#     #TODO sanitize????????
#     return float( nh.split('\n')[0] ) / TERAHASH

####################################################################
def getdifficulty(height: int=None) -> float:
    """
        basically just runs the 'getdifficulty' command
        https://developer.bitcoin.org/reference/rpc/getdifficulty.html
    """
    logging.debug(f"getdifficulty({height=})")

    # this returns the current difficulty
    if height == None:
        if config.RPC_enabled:
            diff = float(run_RPC_command("getdifficulty"))
            logging.debug(f"returning {diff}")
            return diff

        if config.node_path != None:
            diff = os.popen(f"{config.node_path} getdifficulty").read()
            diff = float( diff.split('\n')[0] ) # WHAT THE HELL IS THIS FOR?  TO GET RID OF THE NEWLINE?  hmm. otherwise float cast will fail?
            logging.debug(f"returning {diff}")
            return diff
        
        raise Exception("getdifficulty() called but no node is setup")

    if height > config.height or height < 0:
        return None

    # if a height is given we use getblockheader to find the difficulty at that block
    # first, we need the block hash
    hash = getblockhash(height)
    if hash == None:
        return None

    if config.RPC_enabled:
        diff = run_RPC_command("getblockheader", hash)
        diff = float(diff['difficulty'])
        logging.debug(f"returning {diff}")
        return diff

    if config.node_path != None:
        diff = os.popen(f"{config.node_path} getblockheader {hash}").read()

        try:
            diff = float(json.loads(diff)["difficulty"])
            logging.debug(f"returning {diff}")
            return diff
        except json.decoder.JSONDecodeError:
            # this will fail if the node is unable to return the block time (eg. pruned node)
            logging.debug("json decode error - are you running a pruned node?")
            # TODO what about a pruned node over RPC... we're not catching that possibility in this code... darn-it!
            return None

    raise Exception("getdifficulty() called but no node is setup")

###########################################################################
def avgerage_block_fee(nBlocks = EXPECTED_BLOCKS_PER_DAY) -> int:
    """
        This will return the average fee going back nBlocks using the bitcoin cli at the provided path
    """
    if config.node_path == None:
        return None

    blockheight = int(os.popen(f"{config.node_path} getblockcount").read())

    with output.popup(f"Averaging transactions fees for last {nBlocks} blocks...", closable=False) as p:

        pin.put_input("remaining", value=nBlocks, label="Blocks remaining:")
        pin.put_textarea("feescroller", value='')
        pin.put_input('sofar', value='', label="Average so far:")
        output.put_button("Stop early", color='danger', onclick=lambda: output.close_popup())

        total_fee = 0
        for bdx in range(blockheight-nBlocks, blockheight):
            block_fee = int( os.popen(f"""{config.node_path} getblockstats {bdx} '["totalfee"]'""").read().split(': ')[1].split('\n')[0] )        
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
