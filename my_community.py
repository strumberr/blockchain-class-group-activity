class MyCommunity:
    def __init__(self, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key
        self.peers = {}

    def add_peer(self, peer_public_key):
        peer_id = self._get_peer_id(peer_public_key)
        self.peers[peer_id] = peer_public_key

    def get_peer_by_public_key(self, public_key):
        peer_id = self._get_peer_id(public_key)
        return self.peers.get(peer_id)

    def send_message(self, recipient_public_key, message):
        recipient = self.get_peer_by_public_key(recipient_public_key)
        if recipient:
            # Logic for sending the message to the recipient
            print(f"Message sent to {recipient}: {message}")
            return True
        else:
            return False

    def _get_peer_id(self, public_key):
        
        return public_key

class ValidatorCommunity:
    
    pass

def start_communities(sender_private_key, sender_public_key, receiver_public_key, amount, message):
    my_community = MyCommunity(sender_private_key, sender_public_key)
    my_community.add_peer(receiver_public_key)
    message_status = my_community.send_message(receiver_public_key, message)
    return "success" if message_status else "failure"
