from __future__ import annotations

import random
import typing
from asyncio import Event
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from ipv8.community import Community, CommunitySettings
from ipv8.lazy_community import lazy_wrapper
from ipv8.messaging.payload_dataclass import overwrite_dataclass
from ipv8.messaging.serialization import Payload
from ipv8.types import LazyWrappedHandler, MessageHandlerFunction, Peer

from base64 import b64decode, b64encode

from communities.node_types import node_is_node_type, node_type_to_list, node_type_to_str

from ipv8.peerdiscovery.network import PeerObserver

from ipv8.messaging.payload_dataclass import VariablePayload

from ipv8.messaging.serialization import default_serializer

import jsonpickle

# We are using a custom dataclass implementation.
dataclass = overwrite_dataclass(dataclass)


# identifier message types
IDENTIFIER_REQUEST = 0
IDENTIFIER_RESPONSE = 1

@dataclass
class Identity():
    node_id: int
    peer_public_key: bytes
    node_type: int 
    
    def __init__(self, node_id: int, peer_public_key: str, node_type: int):
        self.node_id = node_id
        self.peer_public_key = peer_public_key
        self.node_type = node_type
    
@dataclass(msg_id=3)
class IdentifierMsg:
    sender: Identity = None
    receiver: Identity = None
    type: bool  = IDENTIFIER_REQUEST


DataclassPayload = typing.TypeVar("DataclassPayload")
AnyPayload = typing.Union[Payload, DataclassPayload]


class BlockchainCommunity(Community, PeerObserver):
    community_id = b"harbourspaceuniverse"

    def __init__(self, settings: CommunitySettings) -> None:
        super().__init__(settings)
        self.event: Event = None  # type:ignore

        self.peers_identity: Dict[bytes, Identity] = {}
        
        self.add_message_handler(IdentifierMsg, self.on_identifier)
        self.network.add_peer_observer(self)


    def node_id_from_peer(self, peer: Peer):
        return self.peers_identity[peer.mid].node_id
    
    def peers_by_node_type(self, node_type: int) -> List[Peer]:
        return [
            peer
            for peer in self.get_peers()
            if node_is_node_type(self.peers_identity.get(peer.mid).node_type or 0, node_type)
        ]

    async def started(
        self, node_id: int, node_type: int
    ) -> None:
        self.node_id = node_id
        self.node_type = node_type
        self.my_identity = Identity(node_id, self.my_peer.mid, node_type)
        
        print(f"[Node {self.node_id}] Started")
        
        return
        
    def on_start(self):
        pass

    def stop(self, delay: int = 0):
        async def delayed_stop():
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
                IdentifierMsg(
                    self.my_identity,
                    payload.sender,
                    IDENTIFIER_RESPONSE
                )
            )
        elif payload.type == IDENTIFIER_RESPONSE:
            self.peers_identity[payload.sender.peer_public_key] = payload.sender
            print(
                f"From Node {self.node_id}: Node {payload.sender.node_id} is {node_type_to_str(payload.sender.node_type)}"
            )
            print(f"{payload.sender}")
        
        return

    def on_peer_added(self, peer: Peer) -> None:
        
        # print(f"[Node {self.node_id}] Peer {peer.mid} added")
        
        self.ez_send(
            peer,
            IdentifierMsg(
                self.my_identity,
                Identity(0, peer.mid, 0),
                IDENTIFIER_REQUEST
            ),
        )
                
        return

    def on_peer_removed(self, peer: Peer) -> None:
       
        print(f"[Node {self.node_id}] Peer {peer.mid} removed")
        self.peers_identity.pop(peer.mid, None) 
        return
    
    
