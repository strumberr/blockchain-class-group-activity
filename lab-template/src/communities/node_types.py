from typing import List

# Community types for the blockchain
CLIENT_NODE = 1
VALIDATOR_NODE = 2
MINER_NODE = 4


def node_is_node_type(node_type: int, node_type_to_check: int) -> bool:
    return node_type & node_type_to_check == node_type_to_check


def node_type_to_list(node_type: int) -> List[str]:
    type = []
    if node_is_node_type(node_type, CLIENT_NODE):
        type.append("Client")
    if node_is_node_type(node_type, VALIDATOR_NODE):
        type.append("Validator")
    if node_is_node_type(node_type, MINER_NODE):
        type.append("Miner")
    return type


def node_type_to_str(node_type: int) -> str:
    type = ""
    if node_is_node_type(node_type, CLIENT_NODE):
        type += (", " if type else "") + "Client"
    if node_is_node_type(node_type, VALIDATOR_NODE):
        type += (", " if type else "") + "Validator"
    if node_is_node_type(node_type, MINER_NODE):
        type += (", " if type else "") + "Miner"
    return type
