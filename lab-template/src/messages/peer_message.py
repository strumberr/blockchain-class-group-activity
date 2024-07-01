from dataclasses import dataclass

import jsonpickle
from ipv8.messaging.payload_dataclass import overwrite_dataclass

# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)


@dataclass
class PeerMessage:
    sender: bytes
    receiver: bytes
    message: str
    nonce: int
    timestamp: int

    def __init__(
        self,
        sender: bytes,
        receiver: bytes,
        message: str,
        nonce: int,
        timestamp: int,
    ):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.nonce = nonce
        self.timestamp = timestamp


@dataclass(msg_id=6)
class SignedPeerMessage:
    """Message for requesting or responding to an identifier"""

    message: PeerMessage
    signature: bytes
    public_key: bytes


def serialize_peer_message(peer_message: PeerMessage) -> bytes:
    return jsonpickle.encode(peer_message).encode()


def deserialize_peer_message(data: bytes) -> PeerMessage:
    return jsonpickle.decode(data.decode())
