import hashlib
import datetime

class Block:
    def __init__(self, index, voter_name, voter_id, candidate, previous_hash, timestamp=None):
        self.index = index
        self.timestamp = timestamp or str(datetime.datetime.now())
        self.voter_name = voter_name
        self.voter_id = voter_id
        self.candidate = candidate
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = (
            str(self.index) +
            self.timestamp +
            self.voter_name +
            self.voter_id +
            self.candidate +
            self.previous_hash
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def masked_id(self):
        vid = self.voter_id
        if len(vid) == 12:
            return f"XXXX-XXXX-{vid[-4:]}"
        elif len(vid) == 10:
            return f"XXXXXX{vid[-4:]}"
        return vid


class Blockchain:
    def __init__(self):
        self.candidates = ["Narendra Modi", "Yogi Adityanath", "Rahul Gandhi"]

    def calculate_hash_for(self, index, timestamp, voter_name, voter_id, candidate, previous_hash):
        block_string = str(index) + timestamp + voter_name + voter_id + candidate + previous_hash
        return hashlib.sha256(block_string.encode()).hexdigest()

    def validate_vote_input(self, voter_name, voter_id, candidate):
        voter_id = voter_id.strip()

        if not voter_id.isdigit():
            return False, "❌ Aadhaar / Voter ID must contain digits only."

        if len(voter_id) == 12:
            id_type = "Aadhaar"
        elif len(voter_id) == 10:
            id_type = "Voter ID"
        else:
            return False, "❌ Please enter a valid 12-digit Aadhaar OR 10-digit Voter ID."

        if candidate not in self.candidates:
            return False, "❌ Invalid candidate selected."

        return True, id_type
