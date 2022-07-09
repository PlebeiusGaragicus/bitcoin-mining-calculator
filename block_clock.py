import logging
import sys
import getopt

import src.data as d

RPC_ip_port = None
RPC_user_pass = None

if __name__ == "__main__":
    try:
      opts, args = getopt.getopt(args=sys.argv[1:], longopts=['help', 'rpcip=', 'rpcuser='])
    except getopt.GetoptError as err:
        #logging.exception(err) # can't use this becuase basicConfig has not been called yet!!!
        print(err)
        print("""#TODO USAGE HERE""")
        exit(1)

    for opt, arg in opts:
        if opt in '--help':
            print("""USAGE""")
            exit(0)
        elif opt == '--rpcip':
            RPC_ip_port = arg
        elif opt == '--rpcuser':
            RPC_user_pass = arg

    # remember: any logging calls before this line will run basicConfig with stupid, default settings and mess up our ability to setup our logger.  Only log from here on down
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s] (%(filename)s @ %(lineno)d) %(message)s",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler('debug.log', mode='w')])

    if config.apikey != None:
        logging.info(f"Luxor API key: {config.apikey}")

    # I do it this way because if you're running it on your node over SSH the webpage won't automatically open
    # Also, this script won't exit when you close the webpage otherwise - probably something to do with the thread running session.hold()
    pywebio.start_server(main, port=8080, debug=True)