import asyncio
from flask import Flask, request, jsonify, render_template
from extract_and_decrypt_messages_module import extract_and_decrypt_messages
from cryptography.hazmat.primitives import serialization, hashes


app = Flask(__name__)


@app.route('/send', methods=['GET', 'POST'])
def send():
    
    if request.method == 'POST':
        
        # parse the body of the request
        data = request.get_json()
        message = data.get("message")
        receiver_public_key = data.get("receiver_public_key")
        
        
        print(f"Message: {message}")
        print(f"Receiver Public Key: {receiver_public_key}")
        
        
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
        
        result = asyncio.run(start_communities(sender_private_key, sender_public_key, receiver_public_key, 1, message))
        
        return jsonify(result)
    
    return "Error: Method not allowed"

# route for getting all messages between sender and receiver
@app.route('/my-messages', methods=['GET'])
def messages():
   
    # from get_blocks import start_communities
    
    # run start_communities asynchronusly
    # result_community = asyncio.run(start_communities())
    
    
    with open("sender_public_key.pem", "rb") as file:
        sender_public_key = serialization.load_pem_public_key(file.read()).public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
    # load receiver_private_key from file
    with open("receiver_private_key.pem", "rb") as file:
        receiver_private_key = serialization.load_pem_private_key(file.read(), password=None)
        
    
    messages_thread = extract_and_decrypt_messages("blocks.json", sender_public_key, receiver_private_key)
    


    
    return render_template('my_messages.html', messages=messages_thread)

if __name__ == '__main__':
    app.run(debug=True)
