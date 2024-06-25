from hashlib import sha256
import time
from block import Blockchain, Block, SignedTransaction, Transaction

class Miner:
    def __init__(self, blockchain, difficulty_target, mempool):
        self.blockchain = blockchain
        self.difficulty_target = difficulty_target
        self.mempool = mempool

    def compute_hash(self, block):
        block_string = f'{block.timestamp}{block.difficulty}{block.nonce}{block.prev_hash}{block.merkle_root}{block.coinbase_tx}'
        return sha256(block_string.encode()).hexdigest()

    def mine_block(self, block):
        while True:
            if int(self.compute_hash(block), 16) < 2 ** 256 / self.difficulty_target:
                print(f"Block mined by miner")
                return
            block.nonce += 1