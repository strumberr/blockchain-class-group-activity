import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Function to load RSA key from file
def load_key_from_file(key_file):
    with open(key_file, 'rb') as f:
        key = RSA.import_key(f.read())
    return key

# Function for message encryption using receiver's public key
def encrypt_message(message, receiver_public_key):
    cipher = PKCS1_OAEP.new(receiver_public_key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

# Function for message decryption using receiver's private key
def decrypt_message(encrypted_message, receiver_private_key):
    cipher = PKCS1_OAEP.new(receiver_private_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message.decode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt and decrypt messages using RSA keys")
    parser.add_argument('sender_private_key_file', type=str, help="Sender's private key file")
    parser.add_argument('sender_public_key_file', type=str, help="Sender's public key file")
    parser.add_argument('receiver_private_key_file', type=str, help="Receiver's private key file")
    parser.add_argument('receiver_public_key_file', type=str, help="Receiver's public key file")
    parser.add_argument('message', type=str, help="Message to encrypt and send")
    args = parser.parse_args()

    # Load keys from files
    sender_private_key = load_key_from_file(args.sender_private_key_file)
    sender_public_key = load_key_from_file(args.sender_public_key_file)
    receiver_private_key = load_key_from_file(args.receiver_private_key_file)
    receiver_public_key = load_key_from_file(args.receiver_public_key_file)

    # Encrypt the message with receiver's public key
    encrypted_message = encrypt_message(args.message, receiver_public_key)

    print(f"Original message: {args.message}")
    print(f"Encrypted message: {encrypted_message}")

    # Decrypt the message with receiver's private key
    decrypted_message = decrypt_message(encrypted_message, receiver_private_key)

    print(f"Decrypted message: {decrypted_message}")

