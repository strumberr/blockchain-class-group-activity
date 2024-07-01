from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import overwrite_dataclass

# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)

# identifier message types
IDENTIFIER_REQUEST = 0
IDENTIFIER_RESPONSE = 1


@dataclass
class Identity:
    """Identity of a node in the network"""

    node_id: int
    peer_public_key: bytes
    node_type: int

    def __init__(self, node_id: int, peer_public_key: str, node_type: int):
        self.node_id = node_id
        self.peer_public_key = peer_public_key
        self.node_type = node_type


@dataclass(msg_id=10)
class IdentifierMsg:
    """Message for requesting or responding to an identifier"""

    sender: Identity = None
    receiver: Identity = None
    type: bool = IDENTIFIER_REQUEST
