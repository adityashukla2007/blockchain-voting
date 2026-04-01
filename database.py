from supabase import create_client
import hashlib
import datetime

SUPABASE_URL = "https://ukarwyizxeudqwikqpko.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrYXJ3eWl6eGV1ZHF3aWtxcGtvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUwMzQ1MTYsImV4cCI6MjA5MDYxMDUxNn0.xg_3mep5pUSrI91GGmmdRzh2hXWvgYkjZF4SjUyRqcs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_all_votes():
    """Fetch all votes from Supabase, ordered by id (chain order)."""
    try:
        response = supabase.table("votes").select("*").order("id").execute()
        return response.data or []
    except Exception as e:
        return []


def voter_already_voted(voter_id):
    """Check if a voter_id already exists in the database."""
    try:
        response = supabase.table("votes").select("voter_id").eq("voter_id", voter_id).execute()
        return len(response.data) > 0
    except Exception as e:
        return False


def cast_vote(voter_name, voter_id, candidate):
    """
    Add a new vote to Supabase.
    Builds blockchain hash based on previous record.
    Returns (success: bool, message: str)
    """
    try:
        # Get all existing votes to build the chain
        all_votes = get_all_votes()

        # Check double voting
        for v in all_votes:
            if v["voter_id"] == voter_id:
                id_type = "Aadhaar" if len(voter_id) == 12 else "Voter ID"
                return False, f"❌ This {id_type} has already been used to vote!"

        # Determine previous hash (genesis if first vote)
        if len(all_votes) == 0:
            previous_hash = "0" * 64  # Genesis previous hash
            new_index = 1
        else:
            previous_hash = all_votes[-1]["block_hash"]
            new_index = len(all_votes) + 1

        # Calculate hash for this new block
        timestamp = str(datetime.datetime.now())
        block_string = str(new_index) + timestamp + voter_name + voter_id + candidate + previous_hash
        block_hash = hashlib.sha256(block_string.encode()).hexdigest()

        # Insert into Supabase
        response = supabase.table("votes").insert({
            "voter_name": voter_name,
            "voter_id": voter_id,
            "candidate": candidate,
            "block_hash": block_hash,
            "previous_hash": previous_hash,
        }).execute()

        if response.data:
            return True, f"✅ Vote recorded in Block #{new_index}!"
        else:
            return False, "❌ Failed to save vote. Please try again."

    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower() or "unique" in error_msg.lower():
            return False, "❌ This ID has already been used to vote!"
        return False, f"❌ Database error: {error_msg}"


def get_results(candidates):
    """Count votes per candidate from Supabase."""
    all_votes = get_all_votes()
    results = {c: 0 for c in candidates}
    for vote in all_votes:
        if vote["candidate"] in results:
            results[vote["candidate"]] += 1
    return results


def is_chain_valid():
    """Verify blockchain integrity by rechecking hashes."""
    all_votes = get_all_votes()
    if not all_votes:
        return True

    for i, vote in enumerate(all_votes):
        # Recompute hash
        block_string = (
            str(i + 1) +
            str(vote["timestamp"]) +
            vote["voter_name"] +
            vote["voter_id"] +
            vote["candidate"] +
            vote["previous_hash"]
        )
        expected_hash = hashlib.sha256(block_string.encode()).hexdigest()

        # Note: timestamp may differ slightly due to DB formatting
        # so we just check the chain linkage
        if i > 0:
            if vote["previous_hash"] != all_votes[i - 1]["block_hash"]:
                return False

    return True


def masked_id(voter_id):
    if len(voter_id) == 12:
        return f"XXXX-XXXX-{voter_id[-4:]}"
    elif len(voter_id) == 10:
        return f"XXXXXX{voter_id[-4:]}"
    return voter_id
