import time
import hashlib
import jsonpickle

import random


def address_from_mid(mid: bytes) -> str:
    return mid.hex()


def mid_from_address(address: str) -> bytes:
    return bytes.fromhex(address)


def hash_bytes(data: bytes) -> str:
    hash_object = hashlib.sha256(data)
    return hash_object.hexdigest()


def hash_dict(data: dict) -> str:
    hash_object = hashlib.sha256(jsonpickle.encode(data).encode())
    return hash_object.hexdigest()


def generate_nonce() -> int:
    return random.randint(1, 2**32)


def serialize_dict(data: dict) -> bytes:
    return jsonpickle.encode(data).encode()
