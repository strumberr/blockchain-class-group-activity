from dataclasses import dataclass
from hashlib import sha256
import json
import time
import asyncio
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from merkle_tree import MerkleTree
from collections import defaultdict
from ipv8.community import Community, CommunitySettings
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

# Custom dataclass implementation
dataclass = overwrite_dataclass(dataclass)

@dataclass
class Transaction:
    """ Represents a basic transaction. """
    sender: str
    receiver: str
    amount: int
    nonce: int = 1
    ts: int = 0

@dataclass
class SignedTransaction:
    """ Represents a signed transaction including a signature and public key. """
    transaction: Transaction
    signature: str
    public_key: str

@dataclass
class BlockMessage:
    """ Represents a block message. """
    timestamp: int
    difficulty: int
    nonce: int
    prev_hash: str
    merkle_root: str
    coinbase_tx: str

class Block:
    """ Represents a block of transactions. """
    def __init__(self, timestamp, difficulty, nonce, prev_hash, merkle_root, coinbase_tx):
        self.timestamp = timestamp
        self.difficulty = '0' * difficulty
        self.nonce = nonce
        self.prev_hash = prev_hash
        self.merkle_root = merkle_root
        self.coinbase_tx = coinbase_tx
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        block_string = f'{self.timestamp}{self.difficulty}{self.nonce}{self.prev_hash}{self.merkle_root}{self.coinbase_tx}'
        return sha256(block_string.encode()).hexdigest()

class Blockchain:
    """ Manages the blockchain and its operations. """
    def __init__(self, node_id, difficulty_target):
        self.node_id = node_id
        self.difficulty_target = difficulty_target
        self.chain = [self.create_genesis_block()]
        self.active_mining = False

    def create_merkle_root(self, transactions):
        """ Create a Merkle root from a list of signed transactions. """
        tree = MerkleTree()
        for signed_tx in transactions:
            tx_string = json.dumps(signed_tx.__dict__, default=lambda o: o.__dict__)
            tree.add_leaf(tx_string)
        return tree.get_root()

    def create_genesis_block(self):
        timestamp = int(time.time())
        difficulty = self.difficulty_target
        nonce = 0
        prev_hash = '0' * 64
        coinbase_tx = SignedTransaction(
            transaction=Transaction(sender="boss", receiver="0", amount=50, nonce=1, ts=timestamp),
            signature="coinbase_signature",
            public_key="coinbase_public_key"
        )
        transactions = [coinbase_tx]
        merkle_root = self.create_merkle_root(transactions)
        return Block(timestamp, difficulty, nonce, prev_hash, merkle_root, json.dumps(coinbase_tx.__dict__, default=lambda o: o.__dict__))

    async def create_new_block(self, transactions):
        timestamp = int(time.time())
        nonce = 0
        prev_hash = self.chain[-1].hash
        merkle_root = self.create_merkle_root(transactions)
        
        # Convert transactions to a JSON serializable format
        transactions_json = [tx.__dict__ for tx in transactions]
        
        new_block = Block(timestamp, self.difficulty_target, nonce, prev_hash, merkle_root, json.dumps(transactions_json))
        
        await self.mine_block(new_block)
        return new_block

        


    async def add_block(self, transactions):
        if len(transactions) % 3 != 0:
            raise ValueError("The number of transactions must be a multiple of 3.")
        
        for i in range(0, len(transactions), 3):
            batch = transactions[i:i+3]
            new_block = await self.create_new_block(batch)
            self.chain.append(new_block)
        return new_block
    
    def compute_hash(self, block, nonce):
        block_string = f'{block.timestamp}{block.difficulty}{nonce}{block.prev_hash}{block.merkle_root}{block.coinbase_tx}'
        return sha256(block_string.encode()).hexdigest()

    def compute_hash(self, block, nonce):
        block_string = f'{block.timestamp}{block.difficulty}{nonce}{block.prev_hash}{block.merkle_root}{block.coinbase_tx}'
        return sha256(block_string.encode()).hexdigest()

    async def mine_block(self, block):
        print(f"Starting mining block {block}")
        
        # Start a timer
        start_time = time.time()
        start_time2 = time.time()
        hashes_computed = 0
        current_nonce = 0
        
        target = '0' * self.difficulty_target
        
        while True:
            self.active_mining = True
            
            
            # Every 2 seconds, print the time elapsed and the number of hashes computed
            if time.time() - start_time > 2:
                print(f"Hashes computed: {hashes_computed}")
                # print the time since start_time was defined and formatted in seconds
                print(f"Time elapsed: {time.time() - start_time2:.2f} seconds")
                
                
                start_time = time.time()
                hashes_computed = 0
                
            
            hash_result = self.compute_hash(block, current_nonce)
            
            if hash_result.startswith(target):
                block.nonce = current_nonce
                block.hash = hash_result
                print(f"Block mined by miner {self.node_id} with hash {block.hash}")
                
                
                # edit the block's nonce and hash
                block.nonce = current_nonce
                block.hash = hash_result
                block.difficulty = self.difficulty_target
                
              
                
                # decode the block and print it
                print(
                    f'{bcolors.OKBLOCK}------------------------------------\n'
                    f"{bcolors.OKBLOCK}Block mined by miner {self.node_id} with hash {block.hash}\n"
                    f'''
                    {bcolors.OKBLOCK}New Block:\n
                    {bcolors.OKBLOCK}Timestamp: {block.timestamp}\n
                    {bcolors.OKBLOCK}Difficulty: {block.difficulty}\n
                    {bcolors.OKBLOCK}Nonce: {block.nonce}\n
                    {bcolors.OKBLOCK}Previous Hash: {block.prev_hash}\n
                    {bcolors.OKBLOCK}Merkle Root: {block.merkle_root}\n
                    {bcolors.OKBLOCK}Transaction: {block.coinbase_tx}\n
                    {bcolors.OKBLOCK}Hash: {block.hash}\n'''
                    f'{bcolors.OKBLOCK}------------------------------------\n'
                )        
                

                # Add the block to the chain
                self.chain.append(block)
                
                # Print all the blocks
                for blk in self.chain:
                    print(blk)
                
                self.active_mining = False
                return
            
            current_nonce += 1
            hashes_computed += 1
            await asyncio.sleep(0)  # Yield control to allow other tasks to run





# Example usage:
# blockchain = Blockchain()
# transactions = [
#     SignedTransaction(
#         transaction=Transaction(sender="user1", receiver="user2", amount=20, nonce=1, ts=int(time.time())),
#         signature="signature1",
#         public_key="public_key1"
#     ),
#     SignedTransaction(
#         transaction=Transaction(sender="user3", receiver="user4", amount=30, nonce=1, ts=int(time.time())),
#         signature="signature2",
#         public_key="public_key2"
#     ),
#     SignedTransaction(
#         transaction=Transaction(sender="user5", receiver="user6", amount=40, nonce=1, ts=int(time.time())),
#         signature="signature3",
#         public_key="public_key3"
#     )
# ]

# new_block = blockchain.add_block(transactions, 1)

# print(f'New Block:\nTimestamp: {new_block.timestamp}\nDifficulty: {new_block.difficulty}\nNonce: {new_block.nonce}\nPrevious Hash: {new_block.prev_hash}\nMerkle Root: {new_block.merkle_root}\nCoinbase Transaction: {new_block.coinbase_tx}\nHash: {new_block.hash}')
