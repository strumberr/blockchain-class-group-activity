from dataclasses import dataclass
from hashlib import sha256
import json
import time
import asyncio
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from merkle_tree import MerkleTree

# Custom dataclass implementation
dataclass = overwrite_dataclass(dataclass)

@dataclass(msg_id=3)  # Add a unique msg_id here
class BlockMessage:
    """ Represents a block message. """
    timestamp: int
    difficulty: int
    nonce: int
    prev_hash: str
    merkle_root: str
    message_tx: str
    block_hash: str

@dataclass
class Message:
    """ Represents a basic message. """
    sender_public_key: str
    receiver_public_key: str
    sender: int
    receiver: int
    message: str
    timestamp: int

@dataclass
class SignedMessage:
    """ Represents a signed message including a signature and public key. """
    message: Message
    signature: str
    public_key: str

class bcolors:
    ONMESSAGE = "\033[95m"
    OKSIGNATURE = "\033[92m"
    BADSIGNATURE = "\033[91m"

    ONBLOCKMESSAGE = "\033[94m"
    OKBLOCK = "\033[92m"

    WARNING = "\033[93m"
    ERROR = "\033[91m"

class Blockchain:
    """ Manages the blockchain and its operations. """
    def __init__(self, node_id, difficulty_target):
        self.node_id = node_id
        self.difficulty_target = difficulty_target
        self.chain = [self.create_genesis_block()]
        self.active_mining = False
        self.community = None  # Will be set by ValidatorCommunity

    def create_merkle_root(self, messages):
        """ Create a Merkle root from a list of signed messages. """
        tree = MerkleTree()
        for signed_msg in messages:
            msg_string = json.dumps(signed_msg.__dict__, default=lambda o: o.__dict__)
            tree.add_leaf(msg_string)
        return tree.get_root()

    def create_genesis_block(self):
        timestamp = int(time.time())
        difficulty = self.difficulty_target
        nonce = 0
        prev_hash = '0' * 64
        
        coinbase_msg = SignedMessage(
            message=Message(sender_public_key="boss_public_key", receiver_public_key="0_public_key", sender=0, receiver=50, message="Genesis message", timestamp=timestamp),
            signature="coinbase_signature",
            public_key="coinbase_public_key"
        )
        
        messages = [coinbase_msg]
        
        merkle_root = self.create_merkle_root(messages)
        
        genesis_block = BlockMessage(
            timestamp=timestamp, 
            difficulty=difficulty, 
            nonce=nonce, 
            prev_hash=prev_hash, 
            merkle_root=merkle_root, 
            message_tx=json.dumps(coinbase_msg.__dict__, default=lambda o: o.__dict__),
            block_hash="00006a347b0bd5ee6c51104c4ed936597371ad02a5f9be8db3ea41be1e963462"
        )
        
        # append the genesis block to the chain
        return genesis_block
    
    async def create_new_block(self, messages):
        timestamp = int(time.time())
        nonce = 0
        prev_hash = self.chain[-1].block_hash
        merkle_root = self.create_merkle_root(messages)
        
        # Convert messages to a JSON serializable format
        messages_json = [msg.__dict__ for msg in messages]

        new_block = BlockMessage(
            timestamp=timestamp, 
            difficulty=self.difficulty_target, 
            nonce=nonce, 
            prev_hash=prev_hash, 
            merkle_root=merkle_root, 
            message_tx=json.dumps(messages_json),
            block_hash="new_block_hash"
        )

        await self.mine_block(new_block)
        return new_block

    async def add_block(self, messages):
        if len(messages) % 3 != 0:
            raise ValueError("The number of messages must be a multiple of 3.")
        
        for i in range(0, len(messages), 3):
            batch = messages[i:i+3]
            new_block = await self.create_new_block(batch)
            self.chain.append(new_block)
        return new_block
    
    def compute_hash(self, block, nonce):
        block_string = f'{block.timestamp}{block.difficulty}{nonce}{block.prev_hash}{block.merkle_root}{block.message_tx}'
        return sha256(block_string.encode()).hexdigest()

    async def mine_block(self, block):
        print(f"Starting mining block {block}")
        
        # Start a timer
        start_time = time.time()
        hashes_computed = 0
        current_nonce = 0
        
        target = '0' * self.difficulty_target
        
        while True:
            self.active_mining = True
            
            # Every 2 seconds, print the time elapsed and the number of hashes computed
            if time.time() - start_time > 2:
                print(f"Hashes computed: {hashes_computed}")
                print(f"Time elapsed: {time.time() - start_time:.2f} seconds")
                start_time = time.time()
                
            hash_result = self.compute_hash(block, current_nonce)
            
            if hash_result.startswith(target):
                block.nonce = current_nonce
                block.block_hash = hash_result
                print(f"Block mined by miner {self.node_id} with hash {block.block_hash}")
                
                print(
                    f'{bcolors.OKBLOCK}------------------------------------\n'
                    f"{bcolors.OKBLOCK}Block mined by miner {self.node_id} with hash {block.block_hash}\n"
                    f'''
                    {bcolors.OKBLOCK}New Block:\n
                    {bcolors.OKBLOCK}Timestamp: {block.timestamp}\n
                    {bcolors.OKBLOCK}Difficulty: {block.difficulty}\n
                    {bcolors.OKBLOCK}Nonce: {block.nonce}\n
                    {bcolors.OKBLOCK}Previous Hash: {block.prev_hash}\n
                    {bcolors.OKBLOCK}Merkle Root: {block.merkle_root}\n
                    {bcolors.OKBLOCK}Message Body: {block.message_tx}\n
                    {bcolors.OKBLOCK}Hash: {block.block_hash}\n'''
                    f'{bcolors.OKBLOCK}------------------------------------\n'
                )      
                
                # Add the block to the chain
                self.chain.append(block)
                
                # Broadcast the block to peers
                await self.community.broadcast_block(block)
                
                self.active_mining = False
                return
            
            current_nonce += 1
            hashes_computed += 1
            await asyncio.sleep(0)
