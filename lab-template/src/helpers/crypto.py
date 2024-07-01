from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def hash(data: bytes) -> str:
    # Create a hash context
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())

    # Update the context with the data
    digest.update(data)

    # Finalize the context and get the digest
    hashed_data = digest.finalize()

    return hashed_data.hex()


def data_encrypt(data: bytes, public_key: str) -> bytes:
    # Load the public key
    public_key_obj = serialization.load_pem_public_key(
        public_key, backend=default_backend()
    )

    # Encrypt the data
    encrypted = public_key_obj.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return encrypted


def data_decrypt(data: bytes, private_key: str) -> bytes:
    # Load the private key
    private_key_obj = serialization.load_pem_private_key(
        private_key,
        password=None,  # Assuming the private key is not password protected
        backend=default_backend(),
    )

    # Decrypt the data
    decrypted = private_key_obj.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return decrypted
