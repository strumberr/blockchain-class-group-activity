import json
import random
import time
from base64 import b64encode, b64decode
from typing import List, Dict
from asyncio import run
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ipv8.configuration import ConfigBuilder, WalkerDefinition, default_bootstrap_defs, Strategy
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.serialization import Payload
from ipv8.peerdiscovery.network import PeerObserver
from ipv8_service import IPv8
from ipv8.types import Peer, MessageHandlerFunction
from ipv8.community import Community, CommunitySettings
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from ipv8.util import run_forever

from utils.helpers import (
    CLIENT_NODE,
    VALIDATOR_NODE,
    node_is_node_type,
    node_type_to_str,
    bcolors,
    Message,
    SignedMessage
)

from block import BlockMessage, Blockchain
from collections import defaultdict
from merkle_tree import MerkleTree
from hashlib import sha256

import asyncio
import argparse




class Message:
    sender_public_key: str
    receiver_public_key: str
    sender: int
    receiver: int
    message: str
    timestamp: int
    signature: str
    

class ValidatorCommunity(Community):
    community_id = b"harbourspaceuniverse"

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)

        self.saved_msgs_hashes = {}

        self.current_block_msgs = []
        self.merkle_tree = MerkleTree()
        self.add_message_handler(SignedMessage, self.on_message)
        self.add_message_handler(BlockMessage, self.on_block_message)
        self.miner_address = b64encode(self.my_peer.public_key.key_to_bin()).decode("utf-8")
        
        self.mempool = []
        self.node_id = 0
        self.difficulty_target = 3
        self.block_size = 3
        self.active_mining = False
        
    async def started(self, node_id) -> None:
        self.node_id = node_id
        print(f"Node ID: {self.node_id}")

        # initialize Block class
        self.blockchain = Blockchain(node_id, self.difficulty_target)
        self.blockchain.community = self  # Link to the community

    def serialize_message(self, msg: Message) -> bytes:
        return json.dumps(msg.__dict__, sort_keys=True).encode()

    def deserialize_message(self, data: bytes) -> Message:
        return Message(**json.loads(data))

    def node_id_from_peer(self, peer: Peer) -> int:
        return int.from_bytes(peer.public_key.key_to_bin()[:4], byteorder="big")

    def generate_msg_id(self, msg: Message):
        return hash((msg.sender, msg.receiver, msg.message, msg.timestamp))

    def verify_signature(self, payload, msg):
        # Verify the signature of the message
        try:
            valid_signature = self.crypto.is_valid_signature(
                self.crypto.key_from_public_bin(b64decode(payload.public_key)),
                self.serialize_message(msg),
                b64decode(payload.signature),
            )
            if not valid_signature:
                print(bcolors.BADSIGNATURE + f"Invalid signature for message {msg.timestamp} from {msg.sender}")
                return False
        except Exception as e:
            print(bcolors.ERROR + f"Error verifying signature: {e}")
            return False

        print(bcolors.OKSIGNATURE + f"Valid message {msg.timestamp} from {msg.sender}")
        return True

    def verify_block_messages(self, block):
        messages = json.loads(block.message_tx)
        for msg_data in messages:
            msg = Message(**msg_data['message'])
            signed_msg = SignedMessage(message=msg, signature=msg_data['signature'], public_key=msg_data['public_key'])
            if not self.verify_signature(signed_msg, msg):
                return False
        return True

    async def broadcast_block(self, block):
        block_message = BlockMessage(
            timestamp=block.timestamp,
            difficulty=block.difficulty,
            nonce=block.nonce,
            prev_hash=block.prev_hash,
            merkle_root=block.merkle_root,
            message_tx=block.message_tx,
            block_hash=block.block_hash
        )
        
        for peer in self.get_peers():
            self.ez_send(peer, block_message)

        print(f"Broadcasted block {block.block_hash} to peers")
    
    

    @lazy_wrapper(SignedMessage)
    async def on_message(self, peer: Peer, payload: SignedMessage) -> None:
        """Handle incoming messages from peers."""

        msg: Message = payload.message

        # Check if the message has already been received
        if self.generate_msg_id(msg) in self.saved_msgs_hashes:
            print(bcolors.WARNING + f"Message {msg.timestamp} already received")
            return

        self.saved_msgs_hashes[self.generate_msg_id(msg)] = True
        print(bcolors.ONMESSAGE + f"Received message {msg.timestamp} from {msg.sender} in a validator community")
    
        # Verify the signature of the message
        if self.verify_signature(payload, msg):
            # add the message to the mempool
            self.mempool.append(msg)
        
        # if the mempool has at least 3 messages, create a block and pass it to mine_block
        if len(self.mempool) >= self.block_size:
            
            if self.blockchain.active_mining:
                print("Mining in progress")
                return
            
            # pick 3 messages from the mempool
            self.current_block_msgs = self.mempool[:self.block_size]
            
            await self.blockchain.create_new_block(self.current_block_msgs)

        for peer in self.get_peers():
            self.ez_send(peer, payload)

    def compute_hash(self, block, nonce):
        block_string = f'{block.timestamp}{block.difficulty}{nonce}{block.prev_hash}{block.merkle_root}{block.message_tx}'
        return sha256(block_string.encode()).hexdigest()

    def create_merkle_root(self, messages):
        """ Create a Merkle root from a list of signed messages. """
        
        messages = self.format_merkle_root(messages)

        tree = MerkleTree()
        for signed_msg in messages:
            msg_string = json.dumps(signed_msg.__dict__, default=lambda o: o.__dict__)
            tree.add_leaf(msg_string)
            
        return tree.get_root()

    def format_merkle_root(self, messages):
        """ Create a Merkle root from a list of signed messages. """
        # Decode the JSON string into a list of dictionaries
        messages_list = json.loads(messages)
        
        reconstructed_messages = []
        for msg_data in messages_list:
            # Recreate the message object
            msg = Message(
                sender_public_key=msg_data['sender_public_key'],
                receiver_public_key=msg_data['receiver_public_key'],
                sender=msg_data['sender'],
                receiver=msg_data['receiver'],
                message=msg_data['message'],
                timestamp=msg_data['timestamp'],
                signature=msg_data['signature']
            )
            
            reconstructed_messages.append(msg)
        
        return reconstructed_messages

    @lazy_wrapper(BlockMessage)
    async def on_block_message(self, peer: Peer, payload: BlockMessage) -> None:
        block = BlockMessage(
            timestamp=payload.timestamp,
            difficulty=payload.difficulty,
            nonce=payload.nonce,
            prev_hash=payload.prev_hash,
            merkle_root=payload.merkle_root,
            message_tx=payload.message_tx,
            block_hash=payload.block_hash
        )

        print(block)
        
        # Verify the block's proof of work by checking if the hash starts with the required number of zeros
        if not block.block_hash.startswith('0' * self.difficulty_target):
            print(bcolors.ERROR + f"Invalid proof of work for block {block.block_hash}")
            return
        else:
            print(bcolors.OKBLOCK + f"Valid proof of work for block {block.block_hash}")
        
        messages_received = block.message_tx
        if self.create_merkle_root(messages_received) != block.merkle_root:
            print(bcolors.ERROR + f"Invalid merkle root for block {block.block_hash}")
            return
        else:
            print(bcolors.OKBLOCK + f"Valid merkle root for block {block.block_hash}")
        
        # verify and compare the block hash with the computed hash
        if block.block_hash != self.compute_hash(block, block.nonce):
            print(bcolors.ERROR + f"Invalid block hash for block {block.block_hash}")
            return
        else:
            print(bcolors.OKBLOCK + f"Valid block hash for block {block.block_hash}")

        # Add the block to the blockchain
        # self.blockchain.chain.append(block)
        # print(f"Added block {block.block_hash} received from peer {peer}")











async def start_communities(node_id) -> None:
    """ Initialize IPv8 and start the communities. """
    
    
    builder = ConfigBuilder().clear_keys().clear_overlays()
    builder.add_key("my peer", "medium", f"ec1.pem")

    builder.add_overlay("ValidatorCommunity", "my peer",
                        [WalkerDefinition(Strategy.RandomWalk,
                                          20, {'timeout': 3.0})],
                        default_bootstrap_defs, {}, [('started', node_id)])
    
    
    
    await IPv8(builder.finalize(), extra_communities={'ValidatorCommunity': ValidatorCommunity}).start()
    await run_forever()
    
    
run(start_communities(1))



# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         prog="Blockchain",
#         description="Code to execute blockchain.",
#         epilog="Designed for A27 Fundamentals and Design of Blockchain-based Systems",
#     )
#     parser.add_argument("node_id", type=int)
#     parser.add_argument("topology", type=str, nargs="?", default="topologies/default.yaml")
#     parser.add_argument("algorithm", type=str, nargs="?", default='echo')
#     parser.add_argument("-docker", action='store_true')

#     args = parser.parse_args()
#     node_id = args.node_id
        
#     run(start_communities(node_id))