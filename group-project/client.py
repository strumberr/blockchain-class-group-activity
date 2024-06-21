import os
import random
import json
from base64 import b64encode
from dataclasses import dataclass
from asyncio import run
import time

from ipv8.community import Community, CommunitySettings
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from ipv8.types import Peer
from ipv8.util import run_forever
from ipv8_service import IPv8

# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)

@dataclass(
    msg_id=1
)  # The value 1 identifies this message and must be unique per community.
class Transaction:
    """ Represents a basic transaction. """
    sender: str
    receiver: str
    amount: int
    nonce: int = 1
    ts: int = int(time.time())

@dataclass(msg_id=2)  # The value 2 identifies this message and must be unique per community.
class SignedTransaction:
    """ Represents a signed transaction including a signature and public key. """
    transaction: Transaction
    signature: str
    public_key: str

class MyCommunity(Community):
    """ Custom community for handling transactions. """

    community_id = b'harbourspaceuniverse'

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.counter = 1
        self.max_messages = 3
        self.add_message_handler(SignedTransaction, self.on_transaction)

    def started(self) -> None:
        """ Start creating transactions periodically. """
        self.register_task("create_transaction", self.create_transaction, interval=1.0, delay=1.0)

    def serialize_transaction(self, tx: Transaction) -> bytes:
        """ Serialize transaction to bytes for storage or transmission. """
        return json.dumps(tx.__dict__, sort_keys=True).encode()

    def deserialize_transaction(self, data: bytes) -> Transaction:
        """ Deserialize bytes back into Transaction object. """
        return Transaction(**json.loads(data))

    def node_id_from_peer(self, peer: Peer) -> int:
        """ Extract node ID from a peer (placeholder implementation). """
        return int.from_bytes(peer.public_key.key_to_bin()[:4], byteorder='big')

    def create_transaction(self) -> None:
        """ Create and send a transaction to a randomly chosen peer. """
        if not self.get_peers():
            print(f'[Node {self.my_peer.mid}] No peers available to send a transaction.')
            return

        peer = random.choice(self.get_peers())
        peer_id = self.node_id_from_peer(peer)

        tx = Transaction(
            b64encode(self.my_peer.public_key.key_to_bin()).decode('utf-8'),
            b64encode(peer.public_key.key_to_bin()).decode('utf-8'),
            10,
            self.counter
        )
        tx_data = self.serialize_transaction(tx)
        signature = b64encode(self.crypto.create_signature(self.my_peer.key, tx_data)).decode('utf-8')

        signed_tx = SignedTransaction(tx, signature, b64encode(self.my_peer.public_key.key_to_bin()).decode('utf-8'))

        self.counter += 1
        print(f'[Node {self.my_peer.mid}] Sending transaction {tx.nonce} to {peer_id}')
        self.ez_send(peer, signed_tx)

        if self.counter > self.max_messages:
            self.cancel_pending_task("create_transaction")

    @lazy_wrapper(SignedTransaction)
    def on_transaction(self, peer: Peer, payload: SignedTransaction) -> None:
        """ Handle incoming signed transactions. """
        print(f"Received signed transaction from {str(peer)}")

async def start_communities() -> None:
    """ Initialize IPv8 and start the MyCommunity. """
    builder = ConfigBuilder().clear_keys().clear_overlays()
    builder.add_key("my peer", "medium", f"ec1.pem")
    builder.add_overlay("MyCommunity", "my peer",
                        [WalkerDefinition(Strategy.RandomWalk,
                                          20, {'timeout': 3.0})],
                        default_bootstrap_defs, {}, [('started',)])
    await IPv8(builder.finalize(), extra_communities={'MyCommunity': MyCommunity}).start()
    await run_forever()

run(start_communities())
