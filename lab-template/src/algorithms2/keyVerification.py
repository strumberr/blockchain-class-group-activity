import json
from collections import defaultdict
from dataclasses import dataclass
from typing import List
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature, decode_dss_signature

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: int
    nonce: int = 1

@dataclass
class SignedTransaction:
    transaction: Transaction
    signature: bytes

class BlockchainNode:
    def __init__(self):
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.key.public_key()
        self.counter = 1
        self.pending_txs: List[Transaction] = []
        self.finalized_txs: List[Transaction] = []
        self.balances = defaultdict(lambda: 1000)

    def create_transaction(self, receiver, amount):
        tx = Transaction(sender=self.public_key_to_hex(), receiver=receiver, amount=amount, nonce=self.counter)
        tx_data = json.dumps(tx.__dict__).encode()
        signature = self.sign_transaction(tx_data)
        
        self.counter += 1
        signed_tx = SignedTransaction(transaction=tx, signature=signature)
        print(f'Created transaction {tx.nonce} to {receiver} with signature {signature.hex()}')
        return signed_tx

    def sign_transaction(self, tx_data):
        signature = self.key.sign(tx_data, ec.ECDSA(hashes.SHA256()))
        return signature

    def verify_transaction(self, payload: SignedTransaction):
        tx = payload.transaction
        tx_data = json.dumps(tx.__dict__).encode()
        signature = payload.signature
        sender_public_key = self.deserialize_public_key(tx.sender)
        
        try:
            sender_public_key.verify(signature, tx_data, ec.ECDSA(hashes.SHA256()))
            print(f"Valid transaction {tx.nonce} from {tx.sender}")
            return True
        except Exception as e:
            print(f"Invalid signature for transaction {tx.nonce} from {tx.sender}: {e}")
            return False

    def public_key_to_hex(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).hex()

    def deserialize_public_key(self, public_key_hex):
        public_key_bytes = bytes.fromhex(public_key_hex)
        return serialization.load_pem_public_key(public_key_bytes)

# Example usage
if __name__ == "__main__":
    # Node 1 creates and signs a transaction
    node1 = BlockchainNode()
    node1_public_key = node1.public_key_to_hex()
    
    # Node 2 initializes and verifies the transaction
    node2 = BlockchainNode()
    transaction = node1.create_transaction(receiver=node2.public_key_to_hex(), amount=10)

    # Node 2 verifies the transaction
    node2.verify_transaction(transaction)
