from dataclasses import dataclass

from ipv8.messaging.payload_dataclass import overwrite_dataclass

# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)

# identifier message types
IDENTIFIER_REQUEST = 0
IDENTIFIER_RESPONSE = 1


@dataclass
class Identity:
    """
    Identity class for nodes in the network

    Attributes:
        node_id (int): Identifier of the node
        mid (bytes): Unique identifier of the peer
        public_key_bin (bytes): Public key of the node decoded to a string
        node_type (int): Type of the node
    """

    node_id: int
    mid: bytes
    public_key_bin: bytes
    node_type: int

    def __init__(self, node_id: int, mid: bytes, public_key_bin: bytes, node_type: int):
        """
        Initializes the identity

        Args:
            node_id (int): Identifier of the node
            mid (bytes): Unique identifier of the node
            public_key_bin (bytes): Public key of the node
            node_type (int): Type of the node
        """
        self.node_id = node_id
        self.mid = mid
        self.public_key_bin = public_key_bin
        self.node_type = node_type


@dataclass(msg_id=10)
class IdentifierMsg:
    """
    Identifier message class

    Attributes:
        sender (Identity): Sender of the message
        receiver (Identity): Receiver of the message
        type (bool): Type of the message
    """

    sender: Identity
    receiver: Identity
    type: bool = IDENTIFIER_REQUEST

    def __init__(self, sender: Identity, receiver: Identity, type: bool):
        """
        Initializes the identifier message

        Args:
            sender (Identity): Sender of the message
            receiver (Identity): Receiver of the message
            type (bool): Type of the message
        """
        self.sender = sender
        self.receiver = receiver
        self.type = type
