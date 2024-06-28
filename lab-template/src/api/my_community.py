import json
import random
from base64 import b64encode
from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.types import Peer

from utils.transaction import MessageBody, SignedMessageBody
from validator_community import ValidatorCommunity

import time


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
        # self.max_messages = 3

    def serialize_message(self, tx: MessageBody) -> bytes:
        """Serialize message to bytes for storage or transmission."""
        return json.dumps(tx.__dict__, sort_keys=True).encode()

    def deserialize_message(self, data: bytes) -> MessageBody:
        """Deserialize bytes back into Transaction object."""
        return MessageBody(**json.loads(data))

    def node_id_from_peer(self, peer: Peer) -> int:
        """Extract node ID from a peer (placeholder implementation)."""
        return int.from_bytes(peer.public_key.key_to_bin()[:4], byteorder="big")

    def send_message(self, sender: str, recipient: str, body: int) -> None:
        """Create and send a transaction."""
        if not self.get_peers():
            print(
                bcolors.ERROR
                + f"[Node {self.my_peer.mid}] No peers available to send a transaction."
            )
            return

        peer = random.choice(self.get_peers())
        peer_id = self.node_id_from_peer(peer)

        tx = MessageBody(
            sender=sender,
            receiver=recipient,
            body=body,
            nonce=self.counter,
            ts=int(time.time()),
        )

        tx_data = self.serialize_message(tx)

        signature = b64encode(
            self.crypto.create_signature(self.my_peer.key, tx_data)
        ).decode("utf-8")

        signed_tx = SignedMessageBody(
            tx,
            signature,
            b64encode(self.my_peer.public_key.key_to_bin()).decode("utf-8"),
        )

        self.counter += 1
        print(
            bcolors.SENDTRANSACTION
            + f"[Node {self.my_peer.mid}] Sending message {tx.nonce} to {peer_id}"
        )
        self.ez_send(peer, signed_tx)
        
        return signed_tx

        # if self.counter > self.max_messages:
        #     print(f"[Node {self.my_peer.mid}] Reached max messages. Stopping.")
    
    # @lazy_wrapper(SignedTransaction)
    # async def on_transaction(self, peer: Peer, payload: SignedTransaction) -> None:
    #     """Handle incoming signed transactions."""
    #     print(
    #         bcolors.ONTRANSACTION
    #         + f"Received signed transaction from {str(peer)} in a client community."
    #     )
    #     for peer in self.get_peers():
    #         self.ez_send(peer, payload)
