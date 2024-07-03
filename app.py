from flask import Flask, request, jsonify
import argparse
import asyncio
from threading import Thread
from my_community import MyCommunity, ValidatorCommunity, start_communities

app = Flask(__name__)



@app.route('/')
def home():
    return "Welcome to the Blockchain Flask app!"

@app.route('/send_message', methods=['POST','GET'])
def send_message():
    data = request.json
    sender_private_key = data['sender_private_key']
    sender_public_key = data['sender_public_key']
    receiver_public_key = data['receiver_public_key']
    amount = data['amount']
    message = data['message']

    # Start communities and send message
    result = start_communities(sender_private_key, sender_public_key, receiver_public_key, amount, message)
    
    if result == "success":
        return jsonify({"status": "Message sent"})
    else:
        return jsonify({"error": "Recipient not found"}), 404



if __name__ == '__main__':
    
    # Start Flask app
    app.run(debug=True)


