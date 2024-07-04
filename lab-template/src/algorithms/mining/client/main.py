from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8.util import run_forever
from ipv8_service import IPv8
from asyncio import run

from ipv8.configuration import get_default_configuration



from validator_community import ValidatorCommunity

from validator_community import ValidatorCommunity

import argparse

import json
import random
from base64 import b64encode
from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.types import Peer
from transaction import Transaction, SignedTransaction
import time 
import random
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

builder = ConfigBuilder().clear_keys().clear_overlays()

class bcolors:
    # BLUE
    SENDTRANSACTION = "\033[94m"
    ERROR = "\033[91m"



class MyCommunity(Community):
    """Custom community for handling transactions."""

    community_id = b"harbourspaceuniverse"

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.counter = 1
        self.max_messages = 3
        # self.overlays = {}
        # self.add_message_handler(SignedTransaction, self.on_transaction)
        self.sender_private_key = None
        self.receiver = None
        self.amount = None
        self.message = None
        self.sender_public_key = None
        

    def started(self, sender_private_key, sender_public_key, receiver, amount, message, builder) -> None:
        """Start creating transactions periodically."""
        self.register_task(
            "create_transaction", self.create_transaction, interval=1.0, delay=1.0
        )
        self.sender_private_key = sender_private_key
        self.receiver_public_key = receiver
        self.amount = amount
        self.message = message
        self.sender_public_key = sender_public_key
        self.builder = builder
        


    def serialize_transaction(self, tx: Transaction) -> bytes:
        """Serialize transaction to bytes for storage or transmission."""
        return json.dumps(tx.__dict__, sort_keys=True).encode()

    def deserialize_transaction(self, data: bytes) -> Transaction:
        """Deserialize bytes back into Transaction object."""
        return Transaction(**json.loads(data))

    def node_id_from_peer(self, peer: Peer) -> int:
        """Extract node ID from a peer (placeholder implementation)."""
        return int.from_bytes(peer.public_key.key_to_bin()[:4], byteorder="big")
    
    def convertToBinary(self, string):
        # without using key_to_bin
        return string.encode('utf-8')

    async def create_transaction(self) -> None:
        """Create and send a transaction to a randomly chosen peer."""


        tx = Transaction(
            sender=b64encode(self.sender_public_key).decode("utf-8"),
            receiver=b64encode(self.convertToBinary(self.receiver_public_key)).decode("utf-8"),
            amount=self.amount,
            nonce=self.counter,
            ts=int(time.time()),
            message=self.message
        )
        
        print(f"Transaction: {tx}")

        tx_data = self.serialize_transaction(tx)

        print(f"Private key: {self.my_peer.key}")
        
        if not self.get_peers():
            print(
                bcolors.ERROR
                + f"[Node {self.my_peer.mid}] No peers available to send a transaction."
            )
            
            return "No peers available to send a transaction."

        peer = random.choice(self.get_peers())
        
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

        # if self.counter > self.max_messages:
        #     self.cancel_pending_task("create_transaction")
        
        self.cancel_pending_task("create_transaction")
            






async def start_communities(sender_private_key, sender_public_key, receiver, amount, message) -> None:
    """ Initialize IPv8 and start the communities. """
    
    
    
    builder.add_key("my peer", "medium", f"ec1.pem")
    
    builder.add_overlay("MyCommunity", "my peer",
                        [WalkerDefinition(Strategy.RandomWalk,
                                          20, {'timeout': 3.0})],
                        default_bootstrap_defs, {}, [('started', 
                                                      sender_private_key, 
                                                      sender_public_key, 
                                                      receiver, amount, 
                                                      message,
                                                      builder)])

    
    await IPv8(builder.finalize(), extra_communities={'MyCommunity': MyCommunity}).start()
    await run_forever()





private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
unencrypted_pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)
pem_public_key = private_key.public_key().public_bytes(
  encoding=serialization.Encoding.PEM,
  format=serialization.PublicFormat.SubjectPublicKeyInfo
)

sender_private_key = unencrypted_pem_private_key
sender_public_key = pem_public_key

print(f"Private key: {sender_private_key}")
print(f"Public key: {sender_public_key}")

receiver_public_key = "r4nd0m5tr1ngReceiver"
amount = 10
message = "Boogers"

run(start_communities(sender_private_key, sender_public_key, receiver_public_key, amount, message))