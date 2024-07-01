from __future__ import annotations

import typing
from asyncio import Event
from typing import Dict, List

from communities.client import ClientCommunity
from communities.validator import ValidatorCommunity
from helpers.node_types import (
    CLIENT_NODE,
    VALIDATOR_NODE,
    node_is_node_type,
    node_type_to_str,
)
from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.serialization import Payload
from ipv8.peerdiscovery.network import PeerObserver
from ipv8.types import MessageHandlerFunction, Peer
from messages.identifier import (
    IDENTIFIER_REQUEST,
    IDENTIFIER_RESPONSE,
    IdentifierMsg,
    Identity,
)

DataclassPayload = typing.TypeVar("DataclassPayload")
AnyPayload = typing.Union[Payload, DataclassPayload]


class BlockchainCommunity(Community, PeerObserver, ClientCommunity):
    community_id = b"harbourspaceuniverst"

    def __init__(self, settings: CommunitySettings) -> None:
        Community.__init__(self, settings)
        self.event: Event = None  # type:ignore

        self.identified_peers: List[Peer] = []
        self.peers_identity: Dict[bytes, Identity] = {}

        self.add_message_handler(IdentifierMsg, self.on_identifier)
        self.network.add_peer_observer(self)

    def node_id_from_peer(self, peer: Peer):
        return self.peers_identity[peer.mid].node_id

    def peers_by_node_type(self, node_type: int) -> List[Peer]:
        return [
            peer
            for peer in self.identified_peers
            if node_is_node_type(
                self.peers_identity.get(peer.mid).node_type or 0, node_type
            )
        ]

    def peer_by_peer_mid(self, peer_mid: bytes) -> Peer:
        return [peer for peer in self.get_peers() if peer.mid == peer_mid][0]

    async def started(self, node_id: int, node_type: int) -> None:
        self.node_id = node_id
        self.node_type = node_type
        self.my_identity = Identity(node_id, self.my_peer.mid, node_type)

        # Init based on node type
        if node_is_node_type(self.node_type, CLIENT_NODE):
            ClientCommunity.__init__(self)

        if node_is_node_type(self.node_type, VALIDATOR_NODE):
            ValidatorCommunity.__init__(self)

        # Start the community based on node type

        if node_is_node_type(self.node_type, CLIENT_NODE):
            await ClientCommunity.started(self)

        if node_is_node_type(self.node_type, VALIDATOR_NODE):
            await ValidatorCommunity.started(self)

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
                IdentifierMsg(self.my_identity, payload.sender, IDENTIFIER_RESPONSE),
            )
        elif payload.type == IDENTIFIER_RESPONSE:
            self.peers_identity[payload.sender.peer_public_key] = payload.sender
            self.identified_peers.append(peer)
            print(
                f"From Node {self.node_id}: Node {payload.sender.node_id} is {node_type_to_str(payload.sender.node_type)}"
            )
            print(f"{payload.sender}")

            self.send_peer_message(peer, "hello from the other side")

        return

    def on_peer_added(self, peer: Peer) -> None:
        self.ez_send(
            peer,
            IdentifierMsg(
                self.my_identity, Identity(0, peer.mid, 0), IDENTIFIER_REQUEST
            ),
        )

        return

    def on_peer_removed(self, peer: Peer) -> None:
        self.peers_identity.pop(peer.mid, None)
        return
