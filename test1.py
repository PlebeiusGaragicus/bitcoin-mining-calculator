RPC_user_pass = "1:2"
RPC_ip_port = "3:4"

#return "curl -s --user {} -X POST http://{} --data-binary '{{\"jsonrpc\":\"1.0\",\"id\":\"0\",\"method\":\"{}\"}}' -H 'Content-Type: application/json'".format(RPC_user_pass, RPC_ip_port, command)
def get_RPC_command(command: str, params: str='') -> str:
    return "curl -s --user {} -X POST http://{} --data-binary '{{\"jsonrpc\":\"1.0\",\"id\":\"0\",\"method\":\"{command}\", \"params\": [ '{params}' ]'}}' -H 'Content-Type: application/json'".format(RPC_user_pass, RPC_ip_port, command, params)

print(get_RPC_command("getblockchainFUCK"))


















# def get_RPC_command() -> str:
#     BASE = "curl -s --user {} -X POST http://{} --data-binary ".format(RPC_user_pass, RPC_ip_port)
#     B2 = '{\"jsonrpc\":\"1.0\",\"id\":\"0\",\"method\":' + command + 


#     getblockchaininfo\"}' -H 'Content-Type: application/json'".format(RPC_user_pass, RPC_ip_port)

# print(get_RPC_command())
