import json
import random
import time
from abc import ABC, abstractmethod
from base64 import b64encode
from typing import List

from algorithms.mining.transaction import SignedTransaction, Transaction
from communities.node_types import VALIDATOR_NODE
from ipv8.types import Peer


class bcolors:
    # BLUE
    SENDTRANSACTION = "\033[94m"
    ERROR = "\033[91m"


class ClientCommunity(ABC):
    """Custom community for handling transactions."""

    def __init__(self) -> None:
        self.counter = 1
        self.max_messages = 3
        # self.overlays = {}
        # self.add_message_handler(SignedTransaction, self.on_transaction)

    async def started(self) -> None:
        """Start creating transactions periodically."""
        self.register_task(
            "create_transaction", self.create_transaction, interval=1.0, delay=1.0
        )

    def serialize_transaction(self, tx: Transaction) -> bytes:
        """Serialize transaction to bytes for storage or transmission."""
        return json.dumps(tx.__dict__, sort_keys=True).encode()

    def deserialize_transaction(self, data: bytes) -> Transaction:
        """Deserialize bytes back into Transaction object."""
        return Transaction(**json.loads(data))

    def node_id_from_peer(self, peer: Peer) -> int:
        """Extract node ID from a peer (placeholder implementation)."""
        return int.from_bytes(peer.public_key.key_to_bin()[:4], byteorder="big")

    def create_transaction(self) -> None:
        """Create and send a transaction to a randomly chosen peer."""
        if not self.get_peers():
            print(
                bcolors.ERROR
                + f"[Node {self.my_peer.mid}] No peers available to send a transaction."
            )
            return

        peer = random.choice(self.peers_by_node_type(VALIDATOR_NODE))
        self.node_id_from_peer(peer)

        tx = Transaction(
            sender=b64encode(self.my_peer.public_key.key_to_bin()).decode("utf-8"),
            receiver=b64encode(peer.public_key.key_to_bin()).decode("utf-8"),
            amount=random.randint(1, 10),
            nonce=self.counter,
            ts=int(time.time()),
        )

        tx_data = self.serialize_transaction(tx)

        signature = b64encode(
            self.crypto.create_signature(self.my_peer.key, tx_data)
        ).decode("utf-8")

        signed_tx = SignedTransaction(
            tx,
            signature,
            b64encode(self.my_peer.public_key.key_to_bin()).decode("utf-8"),
        )

        self.counter += 1
        # print(
        #     bcolors.SENDTRANSACTION
        #     + f"[Node {self.my_peer.mid}] Sending transaction {tx.nonce} to {peer_id}"
        # )

        self.ez_send(peer, signed_tx)

        if self.counter > self.max_messages:
            self.cancel_pending_task("create_transaction")

    @abstractmethod
    def peers_by_node_type(self, node_type: int) -> List[Peer]:
        pass
