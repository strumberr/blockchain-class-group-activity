import json
from abc import ABC, abstractmethod
from base64 import b64decode, b64encode
from collections import defaultdict
from typing import List

from algorithms.mining.block import Blockchain
from algorithms.mining.merkle_tree import MerkleTree
from algorithms.mining.transaction import SignedTransaction, Transaction
from helpers.node_types import VALIDATOR_NODE
from ipv8.lazy_community import lazy_wrapper
from ipv8.types import Peer


class bcolors:
    ONTRANSACTION = "\033[95m"
    OKSIGNATURE = "\033[92m"
    BADSIGNATURE = "\033[91m"

    ONBLOCKMESSAGE = "\033[94m"
    OKBLOCK = "\033[92m"

    WARNING = "\033[93m"
    ERROR = "\033[91m"


class ValidatorCommunity(ABC):
    def __init__(self) -> None:
        self.executed_checks = 0
        self.balances = defaultdict(lambda: 1000)
        self.pending_txs = []
        self.saved_txs_hashes = {}
        self.finalized_txs = []
        self.current_block_txs = []
        self.merkle_tree = MerkleTree()
        self.add_message_handler(SignedTransaction, self.on_transaction)
        # self.add_message_handler(BlockMessage, self.on_block_message)
        self.miner_address = b64encode(self.my_peer.public_key.key_to_bin()).decode(
            "utf-8"
        )

        self.mempool = []
        self.node_id = 0
        self.difficulty_target = 6
        self.block_size = 3
        self.active_mining = False

    async def started(self) -> None:
        self.register_task(
            "check_transactions", self.check_transactions, interval=1.0, delay=1.0
        )

        # initialize Block class
        self.blockchain = Blockchain(node_id, self.difficulty_target)

        # self.register_task("mine_block", self.mine_block_task, interval=5.0, delay=5.0)
        # self.register_task("sync_chain", self.sync_chain, interval=10.0, delay=10.0)

    def serialize_transaction(self, tx: Transaction) -> bytes:
        return json.dumps(tx.__dict__, sort_keys=True).encode()

    def deserialize_transaction(self, data: bytes) -> Transaction:
        return Transaction(**json.loads(data))

    def node_id_from_peer(self, peer: Peer) -> int:
        return int.from_bytes(peer.public_key.key_to_bin()[:4], byteorder="big")

    def generate_tx_id(self, tx: Transaction):
        return hash((tx.sender, tx.receiver, tx.amount, tx.nonce, tx.ts))

    def check_transactions(self) -> None:
        for tx in self.pending_txs:
            if self.balances[tx.sender] - tx.amount >= 0:
                self.balances[tx.sender] -= tx.amount
                self.balances[tx.receiver] += tx.amount
                self.pending_txs.remove(tx)
                self.finalized_txs.append(tx)
                self.current_block_txs.append(tx)
                self.merkle_tree.add_leaf(self.serialize_transaction(tx).decode())

        self.executed_checks += 1

    def verify_signature(self, payload, tx):

        # Verify the signature of the transaction
        try:
            valid_signature = self.crypto.is_valid_signature(
                self.crypto.key_from_public_bin(b64decode(payload.public_key)),
                self.serialize_transaction(tx),
                b64decode(payload.signature),
            )
            if not valid_signature:
                print(
                    bcolors.BADSIGNATURE
                    + f"Invalid signature for transaction {tx.nonce} from {tx.sender}"
                )
                return
        except Exception as e:
            print(bcolors.ERROR + f"Error verifying signature: {e}")
            return

        print(bcolors.OKSIGNATURE + f"Valid transaction {tx.nonce} from {tx.sender}")

        self.pending_txs.append(tx)

        # Send the transaction to another peers
        for peer in self.peers_by_node_type(VALIDATOR_NODE):
            self.ez_send(peer, payload)

    @lazy_wrapper(SignedTransaction)
    async def on_transaction(self, peer: Peer, payload: SignedTransaction) -> None:
        """Handle incoming transactions from peers."""

        tx: Transaction = payload.transaction

        # Check if the transaction has already been received
        if self.generate_tx_id(tx) in self.saved_txs_hashes:
            print(bcolors.WARNING + f"Transaction {tx.nonce} already received")
            return

        self.saved_txs_hashes[self.generate_tx_id(tx)] = True
        print(
            bcolors.ONTRANSACTION
            + f"Received transaction {tx.nonce} from {tx.sender} in a validator community"
        )

        # Verify the signature of the transaction
        self.verify_signature(payload, tx)

        # add the transaction to the mempool
        self.mempool.append(tx)

        print(f"Mempool: {self.mempool}")

        # if the mempool has at least 3 transactions, create a block and bass it to mine_block
        if len(self.mempool) >= self.block_size:

            if self.blockchain.active_mining:
                print("Mining in progress")
                return

            # pick 3 transactions from the mempool
            self.current_block_txs = self.mempool[: self.block_size]

            # print(f"Current block txs: {self.current_block_txs}")

            await self.blockchain.create_new_block(self.current_block_txs)

        for peer in self.peers_by_node_type(VALIDATOR_NODE):
            self.ez_send(peer, payload)

    @abstractmethod
    def peers_by_node_type(self, node_type: int) -> List[Peer]:
        pass
