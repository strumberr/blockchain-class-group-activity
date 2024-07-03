
from typing import List
import time
from dataclasses import dataclass
from ipv8.messaging.payload_dataclass import overwrite_dataclass

# Community types for the blockchain
CLIENT_NODE = 1
VALIDATOR_NODE = 2
MINER_NODE = 4


# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)


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



class bcolors:
    # BLUE
    SENDTRANSACTION = "\033[94m"
    ERROR = "\033[91m"
    
    ONTRANSACTION = "\033[95m"
    OKSIGNATURE = "\033[92m"
    BADSIGNATURE = "\033[91m"

    ONBLOCKMESSAGE = "\033[94m"
    OKBLOCK = "\033[92m"

    WARNING = "\033[93m"
    ERROR = "\033[91m"



@dataclass(msg_id=1)
class Message:
    """ Represents a basic message. """
    sender_public_key: str
    receiver_public_key: str
    sender: int
    receiver: int
    message: str
    timestamp: int

@dataclass(msg_id=2)
class SignedMessage:
    """ Represents a signed message including a signature and public key. """
    message: Message
    signature: str
    public_key: str


class BlockMessage:
    """ Represents a block message. """
    timestamp: int
    difficulty: int
    nonce: int
    prev_hash: str
    merkle_root: str
    message_tx: str
    block_hash: str
    


  

# @dataclass(msg_id=1)  # The value 1 identifies this message and must be unique per community.
# class Transaction:
#     """ Represents a basic transaction. """
#     sender: str
#     receiver: str
#     amount: int
#     nonce: int = 1
#     ts: int = 0

#     def __init__(self, sender: str, receiver: str, amount: int, nonce: int = 1, ts: int = None):
#         self.sender = sender
#         self.receiver = receiver
#         self.amount = amount
#         self.nonce = nonce
#         self.ts = ts if ts is not None else int(time.time())

# @dataclass(msg_id=2)  # The value 2 identifies this message and must be unique per community.
# class SignedTransaction:
#     """ Represents a signed transaction including a signature and public key. """
#     transaction: Transaction
#     signature: str
#     public_key: str