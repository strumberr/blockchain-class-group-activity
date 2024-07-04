import asyncio
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/send', methods=['GET'])
def send():
    # use the keys from the files
    with open("sender_private_key.pem", "rb") as f:
        sender_unencrypted_pem_private_key = f.read()
        
    with open("sender_public_key.pem", "rb") as f:
        sender_pem_public_key = f.read()
        
    with open("receiver_private_key.pem", "rb") as f:
        receiver_unencrypted_pem_private_key = f.read()
        
    with open("receiver_public_key.pem", "rb") as f:
        receiver_pem_public_key = f.read()
        

    sender_private_key = sender_unencrypted_pem_private_key
    sender_public_key = sender_pem_public_key
    receiver_public_key = receiver_pem_public_key
    
    from main import start_communities
    
    result = asyncio.run(start_communities(sender_private_key, sender_public_key, receiver_public_key, 1, "message"))
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
