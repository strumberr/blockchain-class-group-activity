from __future__ import annotations

import typing
from asyncio import Event
from typing import Dict, Set, List

from communities.client import Client

from helpers.node_types import (
    CLIENT_NODE,
    MINER_NODE,
    node_is_node_type,
    node_type_to_str,
)

from base64 import b64encode, b64decode

from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.serialization import Payload
from ipv8.peerdiscovery.network import PeerObserver
from ipv8.types import MessageHandlerFunction, Peer
from communication.identifier import (
    IDENTIFIER_REQUEST,
    IDENTIFIER_RESPONSE,
    IdentifierMsg,
    Identity,
)

from communities.miner import Miner

from helpers import crypto_utils

DataclassPayload = typing.TypeVar("DataclassPayload")
AnyPayload = typing.Union[Payload, DataclassPayload]


class BlockchainCommunity(PeerObserver, Client, Miner, Community):
    community_id = b"harbourspaceuniverst"

    def __init__(self, settings: CommunitySettings) -> None:
        Community.__init__(self, settings)
        self.event: Event = None  # type:ignore

        self.identified_peers: Set[Peer] = set()
        self.peers_identity: Dict[bytes, Identity] = {}
        self.nonces_received: Set[int] = set()

        self.add_message_handler(IdentifierMsg, self.on_identifier)
        self.network.add_peer_observer(self)

    def peers_by_node_type(self, node_type: int) -> List[Peer]:
        return [
            peer
            for peer in self.identified_peers
            if node_is_node_type(self.peers_identity[peer.mid].node_type, node_type)
        ]

    def started(self, node_id: int, node_type: int) -> None:
        self.node_id = node_id
        self.node_type = node_type

        self.my_peer_address = crypto_utils.address_from_mid(self.my_peer.mid)

        self.my_identity = Identity(
            node_id=self.node_id,
            mid=self.my_peer.mid,
            public_key_bin=b64encode(self.my_peer.public_key.key_to_bin()),
            node_type=self.node_type,
        )

        if node_is_node_type(self.node_type, CLIENT_NODE):
            Client.started(self)

        if node_is_node_type(self.node_type, MINER_NODE):
            Miner.started(self)

        print(f"[Node {self.node_id}] Started")

        return

    def on_start(self) -> None:
        pass

    def stop(self, delay: int = 0) -> None:
        async def delayed_stop() -> None:
            print(f"[Node {self.node_id}] Stopping algorithm")
            self.event.set()

        self.register_anonymous_task("delayed_stop", delayed_stop, delay=delay)

    def ez_send(self, peer: Peer, *payloads: AnyPayload, **kwargs) -> None:
        super().ez_send(peer, *payloads, **kwargs)

    def add_message_handler(
        self, msg_num: int | type[AnyPayload], callback: MessageHandlerFunction
    ) -> None:
        super().add_message_handler(msg_num, callback)

    @lazy_wrapper(IdentifierMsg)
    async def on_identifier(self, peer: Peer, payload: IdentifierMsg) -> None:
        if payload.type == IDENTIFIER_REQUEST:
            self.ez_send(
                peer,
                IdentifierMsg(self.my_identity, self.my_identity, IDENTIFIER_RESPONSE),
            )
        elif payload.type == IDENTIFIER_RESPONSE:
            self.peers_identity[peer.mid] = payload.sender
            self.identified_peers.add(peer)

            for i in range(5):
                self.send_signed_message(
                    crypto_utils.address_from_mid(peer.mid), "Hello"
                )

        return

    def on_peer_added(self, peer: Peer) -> None:
        self.ez_send(
            peer, IdentifierMsg(self.my_identity, self.my_identity, IDENTIFIER_REQUEST)
        )
        return

    def on_peer_removed(self, peer: Peer) -> None:
        self.peers_identity.pop(peer.mid, None)
        self.identified_peers.remove(peer)
        return
