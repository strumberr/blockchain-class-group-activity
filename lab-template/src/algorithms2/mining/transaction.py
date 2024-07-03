import time
from dataclasses import dataclass
from ipv8.messaging.payload_dataclass import overwrite_dataclass

from helpers import crypto_utils

# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)


@dataclass
class Transaction:
    """Represents a basic transaction."""

    sender: str
    receiver: str

    # if the transaction is a message between peers, the message will be encrypted
    # we store the hash of the encrypted message
    message: str

    # if the transaction is a money transfer, the amount will be stored
    # we store the amount of money transferred
    amount: int

    nonce: int
    ts: int

    def __init__(
        self,
        sender: str,
        receiver: str,
        message: str = None,
        amount: int = None,
        nonce: int = 1,
        ts: int = None,
    ):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.amount = amount
        self.nonce = nonce if nonce is not None else crypto_utils.generate_nonce()
        self.ts = ts if ts is not None else int(time.time())

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "message": self.message,
            "amount": self.amount,
            "nonce": self.nonce,
            "ts": self.ts,
        }


@dataclass(msg_id=2)
class SignedTransaction:
    """Represents a signed transaction including a signature and public key."""

    transaction: Transaction
    signature: bytes
    public_key_bin: bytes
