from dataclasses import dataclass
from typing import Optional

import time
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from helpers import crypto_utils

from helpers.bcolors import bcolors


# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)


@dataclass
class Message:
    """
    Message class for communication between nodes

    Attributes:
        sender (str): Address of the sender
        receiver (str): Address of the receiver
        message (str): Encrypted message
        nonce (int): Unique identifier for the message (default: sha256 hash of timestamp)
        timestamp (int): Time of the message creation (default: current time)
    """

    sender: str
    receiver: str
    message: str
    nonce: int
    timestamp: int

    def __init__(
        self,
        sender: str,
        receiver: str,
        message: str,
        nonce: Optional[int] = None,
        timestamp: Optional[int] = None,
    ):
        """
        Initializes the message

        Args:
            sender (str): Address of the sender
            receiver (str): Address of the receiver
            message (str): Encrypted message
            nonce (int): Unique identifier for the message (default: sha256 hash of timestamp)
            timestamp (int): Time of the message creation (default: current time)
        """

        print(
            bcolors.CYAN
            + f"Message from {sender} to {receiver}: {message}"
            + bcolors.RESET
        )

        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.nonce = nonce if nonce is not None else crypto_utils.generate_nonce()
        self.timestamp = timestamp if timestamp is not None else int(time.time())

    def to_dict(self) -> dict:
        """
        Converts the message to a dictionary

        Returns:
            dict: Dictionary representation of the message
        """
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "message": self.message,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
        }


@dataclass(msg_id=6)
class SignedMessage:
    """
    Message for requesting or responding to an identifier

    Attributes:
        sender (str): Address of the sender
        receiver (str): Address of the receiver
        content (Message): Message object
        signature (str): Signature of the message
        nonce (int): Unique identifier for the message (default: sha256 hash of timestamp)
        timestamp (int): Time of the message creation (default: current time)
    """

    sender: str
    receiver: str
    content: Message
    signature: bytes
    public_key_bin: bytes
    nonce: int
    timestamp: int

    def __init__(
        self,
        sender: str,
        receiver: str,
        content: Message,
        signature: bytes,
        public_key_bin: bytes,
        nonce: Optional[int] = None,
        timestamp: Optional[int] = None,
    ):
        """
        Initializes the signed message

        Args:
            sender (str): Address of the sender
            receiver (str): Address of the receiver
            content (Message): Message object
            signature (bytes): Signature of the message
            public_key_bin (bytes): Public key of the original sender in binary format
            nonce (int): Unique identifier for the message (default: sha256 hash of timestamp)
            timestamp (int): Time of the message creation (default: current time)
        """

        print(
            bcolors.CYAN
            + f"Signed message from {sender} to {receiver}: {content.message}"
            + bcolors.RESET
        )

        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.signature = signature
        self.public_key_bin = public_key_bin
        self.nonce = nonce if nonce is not None else crypto_utils.generate_nonce()
        self.timestamp = timestamp if timestamp is not None else int(time.time())

    def to_dict(self) -> dict:
        """
        Converts the signed message to a dictionary

        Returns:
            dict: Dictionary representation of the signed message
        """

        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content.to_dict(),
            "signature": self.signature,
            "original_sender_public_key": self.original_sender_public_key,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
        }
