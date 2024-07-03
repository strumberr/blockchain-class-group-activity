## Overview

Scripts for RSA key generation, message encryption, and decryption.

## Usage

### Generate RSA Key Pairs

```bash
python generate_keys.py sender_private.pem sender_public.pem
python generate_keys.py receiver_private.pem receiver_public.pem
```


### Encrypt a Message
```bash
python sender_encrypt.py receiver_public.pem "Hello, this is a secret message" encrypted_message.bin
```

Replace "Hello, this is a secret message" with your message. The encrypted message will be saved to encrypted_message.bin.

### Decrypt a Message
```bash
python receiver_decrypt.py receiver_private.pem encrypted_message.bin decrypted_message.txt
```
