import argparse
from Crypto.PublicKey import RSA

# Function to generate RSA key pair and save to files
def generate_and_save_key_pair(private_key_file, public_key_file):
    key = RSA.generate(2048)  # Generate a 2048-bit RSA key pair
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    # Save private key to file
    with open(private_key_file, 'wb') as f:
        f.write(private_key)

    # Save public key to file
    with open(public_key_file, 'wb') as f:
        f.write(public_key)

    return private_key, public_key

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RSA key pair and save to files")
    parser.add_argument('private_key_file', type=str, help="File to save private key")
    parser.add_argument('public_key_file', type=str, help="File to save public key")
    args = parser.parse_args()

    # Generate and save keys
    generate_and_save_key_pair(args.private_key_file, args.public_key_file)

    print(f"RSA key pair generated and saved to files:")
    print(f"Private key: {args.private_key_file}")
    print(f"Public key: {args.public_key_file}")
