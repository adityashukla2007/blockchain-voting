import hashlib
import datetime

# ============================================================
# BLOCK CLASS - Think of this as ONE page in a notebook
# Each vote becomes one block (one page)
# ============================================================
class Block:
    def __init__(self, index, voter_name, voter_id, candidate, previous_hash):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.voter_name = voter_name
        self.voter_id = voter_id                        # PRIMARY KEY - Aadhaar / Voter ID
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


# ============================================================
# BLOCKCHAIN CLASS - The full notebook with all pages
# ============================================================
class Blockchain:
    def __init__(self):
        self.chain = []
        self.voted_ids = []    # Tracks Aadhaar/VoterIDs that already voted
        self.candidates = ["Narendra Modi", "Yogi Adityanath", "Rahul Gandhi"]
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, "SYSTEM", "000000000000", "GENESIS BLOCK - Chain Started", "0")
        self.chain.append(genesis)

    def add_vote(self, voter_name, voter_id, candidate):
        voter_id = voter_id.strip()

        if not voter_id.isdigit():
            return False, "❌ Aadhaar / Voter ID must contain digits only. No letters or spaces."

        if len(voter_id) == 12:
            id_type = "Aadhaar"
        elif len(voter_id) == 10:
            id_type = "Voter ID"
        else:
            return False, "❌ Please enter a valid 12-digit Aadhaar OR 10-digit Voter ID."

        if voter_id in self.voted_ids:
            return False, f"❌ This {id_type} has already been used to vote! Double voting is not allowed."

        if candidate not in self.candidates:
            return False, "❌ Invalid candidate selected."

        previous_block = self.chain[-1]
        new_index = len(self.chain)
        new_block = Block(new_index, voter_name.strip(), voter_id, candidate, previous_block.hash)

        self.chain.append(new_block)
        self.voted_ids.append(voter_id)

        return True, f"✅ Vote recorded in Block #{new_index} using {id_type}!"

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_results(self):
        results = {candidate: 0 for candidate in self.candidates}
        for block in self.chain[1:]:
            if block.candidate in results:
                results[block.candidate] += 1
        return results

    def get_chain_data(self):
        chain_data = []
        for block in self.chain:
            chain_data.append({
                "Block #": block.index,
                "Voter Name": block.voter_name,
                "Voter ID (Masked)": block.masked_id(),
                "Voted For": block.candidate,
                "Time": block.timestamp,
                "Hash": block.hash[:20] + "...",
                "Previous Hash": block.previous_hash[:20] + "..."
            })
        return chain_data
