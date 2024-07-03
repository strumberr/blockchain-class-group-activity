===================
RSA Messaging App
===================

1. Generate RSA Key Pair
-------------------------

To generate RSA key pairs for both sender and receiver:

    python generate_keys.py sender_private.pem sender_public.pem
    python generate_keys.py receiver_private.pem receiver_public.pem

2. Encrypt and Decrypt Messages
--------------------------------

To encrypt a message using the sender's private key and the receiver's public key, and then decrypt it using the receiver's private key:

    python send_receive_messages.py sender_private.pem sender_public.pem receiver_private.pem receiver_public.pem "Hello, this is a secret message!"

Replace `"Hello, this is a secret message!"` with the actual message you want to encrypt and send.
