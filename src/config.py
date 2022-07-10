# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
"""
    This module contains the global variables used in the project
"""

node_path = None
pruned = None
pruned_height = None

RPC_enabled = None
RPC_ip_port = None
RPC_user_pass = None

cookie=None

# TODO change these to 0, not none.  Init to a safe state that won't cause an error when the user tinkers with the input fields before loading state from the network completes.
height = None
difficulty = None
price = None

# the number of projections that we've run.
# so we can increment the number when they are all displayed.
analysis_number = 0

# Luxor's API key
apikey = None
