import argparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Function to load RSA private key from file
def load_private_key_from_file(key_file):
    with open(key_file, 'rb') as f:
        key = RSA.import_key(f.read())
    return key

# Function for message decryption using receiver's private key
def decrypt_message(encrypted_message, receiver_private_key):
    try:
        cipher = PKCS1_OAEP.new(receiver_private_key)
        decrypted_message = cipher.decrypt(encrypted_message)
        return decrypted_message.decode()
    except (ValueError, TypeError):
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decrypt message using receiver's private key from file and save decrypted message to file")
    parser.add_argument('receiver_private_key_file', type=str, help="Receiver's private key file")
    parser.add_argument('input_file', type=str, help="File containing the encrypted message")
    parser.add_argument('output_file', type=str, help="File to save the decrypted message")
    args = parser.parse_args()

    # Load receiver's private key from file
    receiver_private_key = load_private_key_from_file(args.receiver_private_key_file)

    # Read encrypted message from file
    with open(args.input_file, 'rb') as f:
        encrypted_message = f.read()

    # Decrypt the encrypted message with receiver's private key
    decrypted_message = decrypt_message(encrypted_message, receiver_private_key)

    if decrypted_message is not None:
        print(f"Decrypted message: {decrypted_message}")

        # Save decrypted message to file
        with open(args.output_file, 'w') as f:
            f.write(decrypted_message)
        
        print(f"Decrypted message saved to: {args.output_file}")
    else:
        print("Failed to decrypt the message. Check if the correct private key is used.")

