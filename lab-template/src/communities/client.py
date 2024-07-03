import random
import time
from abc import ABC, abstractmethod
from typing import List, Dict

from helpers.bcolors import bcolors
from helpers import crypto_utils
from helpers.node_types import CLIENT_NODE, MINER_NODE
from ipv8.lazy_community import lazy_wrapper
from ipv8.types import Peer

from communication.transaction import Transaction, SignedTransaction

from base64 import b64encode, b64decode

from communication.message import (
    Message,
    SignedMessage,
)

from ipv8.community import Community


class Client(Community, ABC):
    """Client node of the blockchain network"""

    def started(self) -> None:
        """Initializes the Client node"""
        self.max_messages = 3
        self.add_message_handler(SignedMessage, self.on_signed_message)

    def send_signed_message(self, peer_address: str, message: str):
        """Generates a message and propagates it to the network."""

        if not self.peers_by_node_type(MINER_NODE):
            print(
                bcolors.ERROR
                + f"[Node {self.my_peer.mid}] No miner peers available to send a transaction."
                + bcolors.RESET
            )
            return

        sender = self.my_peer_address
        receiver = peer_address

        # encrypt the message // pending
        encrypted_message = message

        message_obj = Message(
            sender=sender,
            receiver=receiver,
            message=encrypted_message,
            nonce=crypto_utils.generate_nonce(),
            timestamp=int(time.time()),
        )
        miner_peer = random.choice(self.peers_by_node_type(MINER_NODE))
        miner_address = crypto_utils.address_from_mid(miner_peer.mid)

        signed_message_obj = SignedMessage(
            sender=sender,
            receiver=miner_address,
            content=message_obj,
            signature=self.crypto.create_signature(
                self.my_peer.key, crypto_utils.serialize_dict(message_obj.to_dict())
            ),
            public_key_bin=b64encode(self.my_peer.public_key.key_to_bin()),
            nonce=crypto_utils.generate_nonce(),
            timestamp=int(time.time()),
        )
        self.ez_send(miner_peer, signed_message_obj)

        transaction_obj = Transaction(
            sender=sender,
            receiver=receiver,
            message=encrypted_message,
            amount=0,
            nonce=crypto_utils.generate_nonce(),
            ts=int(time.time()),
        )

        signed_transaction_obj = SignedTransaction(
            transaction=transaction_obj,
            signature=self.crypto.create_signature(
                self.my_peer.key, crypto_utils.serialize_dict(transaction_obj.to_dict())
            ),
            public_key=b64encode(self.my_peer.public_key.key_to_bin()),
        )

        self.ez_send(miner_peer, signed_transaction_obj)

    @abstractmethod
    def peers_by_node_type(self, node_type: int) -> List[Peer]:
        pass

    @lazy_wrapper(SignedMessage)
    def on_signed_message(self, peer: Peer, payload: SignedMessage) -> None:
        """Handles incoming messages."""

        message: Message = payload.content
        nonce = message.nonce

        # Check if the transaction has already been received
        if nonce in self.nonces_received:
            print(bcolors.WARNING + f"Message already received" + bcolors.RESET)
            return

        self.nonces_received.add(nonce)

        # Check the signature of the message

        public_key_bin = payload.public_key_bin

        try:
            valid_signature = self.crypto.is_valid_signature(
                self.crypto.key_from_public_bin(b64decode(public_key_bin)),
                crypto_utils.serialize_dict(message.to_dict()),
                payload.signature,
            )

            if not valid_signature:
                print(
                    bcolors.ERROR
                    + f"Invalid signature for message {message.nonce} from {message.sender}"
                    + bcolors.RESET
                )
                return
        except Exception as e:
            print(bcolors.ERROR + f"Error verifying signature: {e}" + bcolors.RESET)
            return

        # Pending: decrypt the message
        if message.receiver == self.my_peer_address:
            print(
                bcolors.GREEN
                + f"Message {message.nonce} received: {message.message}"
                + bcolors.RESET
            )

        # Propagate the message to the network
        for peer in self.peers_by_node_type(MINER_NODE):
            self.ez_send(peer, payload)
