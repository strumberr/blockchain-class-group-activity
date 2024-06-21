import json
from base64 import b64decode
from collections import defaultdict
from dataclasses import dataclass
from asyncio import run
import time
from hashlib import sha256

from ipv8.community import Community, CommunitySettings
from ipv8.configuration import (
    ConfigBuilder,
    Strategy,
    WalkerDefinition,
    default_bootstrap_defs,
)
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
    ts: int = time.time()

@dataclass(msg_id=2)  # The value 2 identifies this message and must be unique per community.
class SignedTransaction:
    """ Represents a signed transaction including a signature and public key. """
    transaction: Transaction
    signature: str
    public_key: str

class MerkleTree:
    """ Implementation of a Merkle Tree for storing transaction hashes. """

    def __init__(self):
        self.leaves = []
        self.levels = []

    def add_leaf(self, data, do_hash=True):
        """ Add a leaf to the Merkle Tree, optionally hashing the data. """
        if do_hash:
            data = sha256(data.encode('utf-8')).hexdigest()
        self.leaves.append(data)
        self.build_tree()

    def build_tree(self):
        """ Build the Merkle Tree from the leaves. """
        self.levels = [self.leaves]
        current_level = self.leaves
        while len(current_level) > 1:
            new_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                new_level.append(sha256((left + right).encode('utf-8')).hexdigest())
            current_level = new_level
            self.levels.append(current_level)

    def get_root(self):
        """ Get the root hash of the Merkle Tree. """
        if self.levels:
            return self.levels[-1][0]
        return None

class ValidatorCommunity(Community):
    """ Custom community for validating transactions. """

    community_id = b"harbourspaceuniverse"

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.executed_checks = 0
        self.balances = defaultdict(lambda: 1000)
        self.pending_txs = []
        self.saved_txs_hashes = {}
        self.finalized_txs = []
        self.merkle_tree = MerkleTree()
        self.add_message_handler(SignedTransaction, self.on_transaction)

    def started(self) -> None:
        """ Start periodic transaction checks. """
        self.register_task(
            "check_transactions", self.check_transactions, interval=1.0, delay=1.0
        )

    def serialize_transaction(self, tx: Transaction) -> bytes:
        """ Serialize transaction to bytes for storage or transmission. """
        return json.dumps(tx.__dict__, sort_keys=True).encode()

    def deserialize_transaction(self, data: bytes) -> Transaction:
        """ Deserialize bytes back into Transaction object. """
        return Transaction(**json.loads(data))

    def node_id_from_peer(self, peer: Peer) -> int:
        """ Extract node ID from a peer (placeholder implementation). """
        return int.from_bytes(peer.public_key.key_to_bin()[:4], byteorder="big")

    def generate_tx_id(self, tx: Transaction):
        """ Generate a unique ID for a transaction based on its attributes. """
        return hash((tx.sender, tx.receiver, tx.amount, tx.nonce, tx.ts))

    def check_transactions(self) -> None:
        """ Process pending transactions and update balances. """
        for tx in self.pending_txs:
            if self.balances[tx.sender] - tx.amount >= 0:
                self.balances[tx.sender] -= tx.amount
                self.balances[tx.receiver] += tx.amount
                self.pending_txs.remove(tx)
                self.finalized_txs.append(tx)
                self.merkle_tree.add_leaf(self.serialize_transaction(tx).decode())

        self.executed_checks += 1

    @lazy_wrapper(SignedTransaction)
    async def on_transaction(self, peer: Peer, payload: SignedTransaction) -> None:
        """ Handle incoming signed transactions. """
        tx: Transaction = payload.transaction

        if self.generate_tx_id(tx) in self.saved_txs_hashes:
            print(f"Transaction {tx.nonce} already received")
            return

        self.saved_txs_hashes[self.generate_tx_id(tx)] = True
        print(self.saved_txs_hashes)

        # Verify the signature
        try:
            valid_signature = self.crypto.is_valid_signature(
                self.crypto.key_from_public_bin(b64decode(payload.public_key)),
                self.serialize_transaction(tx),
                b64decode(payload.signature),
            )
            if not valid_signature:
                print(f"Invalid signature for transaction {tx.nonce} from {tx.sender}")
                return
        except Exception as e:
            print(f"Error verifying signature: {e}")
            return

        print(f"Valid transaction {tx.nonce} from {tx.sender}")

        self.pending_txs.append(tx)

        # Gossip to other nodes
        for peer in self.get_peers():
            self.ez_send(peer, payload)

async def start_communities() -> None:
    """ Initialize IPv8 and start the ValidatorCommunity. """
    builder = ConfigBuilder().clear_keys().clear_overlays()
    builder.add_key("validator", "medium", f"ec2.pem")
    builder.add_overlay(
        "ValidatorCommunity",
        "validator",
        [WalkerDefinition(Strategy.RandomWalk, 20, {"timeout": 3.0})],
        default_bootstrap_defs,
        {},
        [("started",)],
    )
    await IPv8(
        builder.finalize(), extra_communities={"ValidatorCommunity": ValidatorCommunity}
    ).start()
    await run_forever()

run(start_communities())
