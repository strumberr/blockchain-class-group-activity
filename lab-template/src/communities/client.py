import random
import time
from abc import ABC, abstractmethod
from typing import List

from helpers.bcolors import bcolors
from helpers.crypto import hash
from helpers.node_types import CLIENT_NODE
from ipv8.lazy_community import lazy_wrapper
from ipv8.types import Peer
from messages.peer_message import (
    PeerMessage,
    SignedPeerMessage,
    serialize_peer_message,
)


class ClientCommunity(ABC):
    """Custom community for handling transactions."""

    def __init__(self) -> None:
        self.counter = 1
        self.max_messages = 3
        self.peer_messages_received = {}

        self.add_message_handler(SignedPeerMessage, self.on_peer_message)

    async def started(self) -> None:
        return

    def send_peer_message(self, peer: Peer, message: str):
        """Generates a message and propagates it to the network."""

        if not self.peers_by_node_type(CLIENT_NODE):
            print(
                bcolors.ERROR
                + f"[Node {self.my_peer.mid}] No peers available to send a transaction."
                + bcolors.RESET
            )
            return

        sender = self.my_peer.mid
        receiver = peer.mid

        # Encrypt the  // Pending

        peer_message = PeerMessage(
            sender=sender,
            receiver=receiver,
            message=message,
            nonce=self.counter,
            timestamp=int(time.time()),
        )

        miner_peer = random.choice(self.peers_by_node_type(CLIENT_NODE))
        signed_peer_message = SignedPeerMessage(
            peer_message,
            self.crypto.create_signature(
                self.my_peer.key, serialize_peer_message(peer_message)
            ),
            sender,
        )

        self.counter += 1

        self.ez_send(miner_peer, signed_peer_message)

    @abstractmethod
    def peers_by_node_type(self, node_type: int) -> List[Peer]:
        pass

    @lazy_wrapper(SignedPeerMessage)
    def on_peer_message(self, peer: Peer, payload: SignedPeerMessage) -> None:
        """Handles incoming messages."""

        message = payload.message

        # Check if the transaction has already been received
        if hash(serialize_peer_message(message)) in self.peer_messages_received:
            print(bcolors.WARNING + f"Message already received" + bcolors.RESET)
            return

        self.peer_messages_received[hash(serialize_peer_message(message))] = message

        # # Check the signature of the message

        # try:
        #     valid_signature = self.crypto.is_valid_signature(
        #         self.crypto.key_from_public_bin(public_key),
        #         serialize_peer_message(message),
        #         signature,
        #     )

        #     if not valid_signature:
        #         print(
        #             f"Invalid signature for message {message.nonce} from {message.sender}"
        #         )
        #         return
        # except Exception as e:
        #     print(f"Error: {e}")
        #     return

        # Decrypt the message
        if message.receiver == self.my_peer.mid:

            # decrypt the message // pending
            message_decrypted = message.message

            print(
                bcolors.OK
                + f"Received message {message.nonce} from {message.sender}: {message_decrypted}"
                + bcolors.RESET
            )

        # Propagate the message to the network
        for peer in self.peers_by_node_type(CLIENT_NODE):
            self.ez_send(peer, payload)
