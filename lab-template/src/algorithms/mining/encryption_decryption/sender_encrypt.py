import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Function to load RSA public key from file
def load_public_key_from_file(key_file):
    with open(key_file, 'rb') as f:
        key = RSA.import_key(f.read())
    return key

# Function for message encryption using receiver's public key
def encrypt_message(message, receiver_public_key):
    cipher = PKCS1_OAEP.new(receiver_public_key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt message using receiver's public key and save to file")
    parser.add_argument('receiver_public_key_file', type=str, help="Receiver's public key file")
    parser.add_argument('message', type=str, help="Message to encrypt and send")
    parser.add_argument('output_file', type=str, help="File to save the encrypted message")
    args = parser.parse_args()

    # Load receiver's public key from file
    receiver_public_key = load_public_key_from_file(args.receiver_public_key_file)

    # Encrypt the message with receiver's public key
    encrypted_message = encrypt_message(args.message, receiver_public_key)

    # Save encrypted message to file
    with open(args.output_file, 'wb') as f:
        f.write(encrypted_message)

    print(f"Original message: {args.message}")
    print(f"Encrypted message saved to: {args.output_file}")

