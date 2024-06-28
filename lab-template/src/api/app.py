from flask import Flask, request, jsonify
import asyncio
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8_service import IPv8
from my_community import MyCommunity  # Ensure this matches the file name where MyCommunity is defined
from ipv8.configuration import ConfigBuilder, Strategy, WalkerDefinition, default_bootstrap_defs
from ipv8.util import run_forever
from ipv8_service import IPv8
from asyncio import run

app = Flask(__name__)

@app.route('/api/send-message', methods=['POST'])
def create_message():
    data = request.get_json()
    sender = data['sender']
    recipient = data['recipient']
    body = data['body']
    
    
    
    
    
    
    
if __name__ == '__main__':
    app.run(debug=True)
