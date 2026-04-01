import streamlit as st
from blockchain import Blockchain

st.set_page_config(
    page_title="BlockVote - Blockchain Voting",
    page_icon="🗳️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        font-family: 'Georgia', serif;
    }
    .subtitle {
        text-align: center;
        color: #aaa;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .block-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(0,210,255,0.3);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .genesis-card {
        background: rgba(255,215,0,0.08);
        border: 1px solid rgba(255,215,0,0.4);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00d2ff;
        border-bottom: 2px solid #7b2ff7;
        padding-bottom: 5px;
        margin: 20px 0 15px 0;
    }
    .info-box {
        background: rgba(0,210,255,0.1);
        border-left: 4px solid #00d2ff;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        font-size: 0.95rem;
        color: #ddd;
    }
    .warning-box {
        background: rgba(255,165,0,0.1);
        border-left: 4px solid orange;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        font-size: 0.9rem;
        color: #ddd;
    }
    .valid-badge {
        background: #00c853;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    .invalid-badge {
        background: #d50000;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize blockchain in session
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()

bc = st.session_state.blockchain

# Header
st.markdown('<div class="main-title">🗳️ BlockVote</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Blockchain-Based Voting System | Aadhaar-Verified • Transparent • Tamper-Proof</div>', unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns([1.2, 1.2, 1])

# ------ COLUMN 1: CAST VOTE ------
with col1:
    st.markdown('<div class="section-title">📥 Cast Your Vote</div>', unsafe_allow_html=True)

    st.markdown('<div class="info-box">🔒 Your Aadhaar / Voter ID is your unique key. No two people can vote with the same ID.</div>', unsafe_allow_html=True)
    st.markdown('<div class="warning-box">🛡️ <b>Privacy:</b> Your ID is masked in the blockchain explorer. Only last 4 digits are shown.</div>', unsafe_allow_html=True)

    voter_name = st.text_input("👤 Full Name", placeholder="e.g. Rahul Sharma")

    id_type_choice = st.radio("🪪 ID Type", ["Aadhaar Number (12 digits)", "Voter ID (10 digits)"], horizontal=True)

    if "Aadhaar" in id_type_choice:
        voter_id = st.text_input("🔢 Aadhaar Number", placeholder="Enter 12-digit Aadhaar", max_chars=12)
        st.caption("Example: 123456789012")
    else:
        voter_id = st.text_input("🔢 Voter ID", placeholder="Enter 10-digit Voter ID", max_chars=10)
        st.caption("Example: 1234567890")

    candidate = st.selectbox("🎯 Select Candidate", bc.candidates)

    if st.button("✅ Submit My Vote", use_container_width=True):
        if not voter_name.strip():
            st.error("Please enter your full name!")
        elif not voter_id.strip():
            st.error("Please enter your Aadhaar / Voter ID!")
        else:
            success, message = bc.add_vote(voter_name.strip(), voter_id.strip(), candidate)
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

    st.markdown("---")
    st.markdown("### 📊 Live Stats")
    total_votes = len(bc.chain) - 1
    st.metric("Total Votes Cast", total_votes)
    st.metric("Total Blocks in Chain", len(bc.chain))
    is_valid = bc.is_chain_valid()
    st.markdown("**Chain Integrity:**")
    if is_valid:
        st.markdown('<span class="valid-badge">✅ CHAIN IS VALID</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="invalid-badge">❌ CHAIN TAMPERED!</span>', unsafe_allow_html=True)

# ------ COLUMN 2: RESULTS ------
with col2:
    st.markdown('<div class="section-title">📈 Live Election Results</div>', unsafe_allow_html=True)

    results = bc.get_results()
    total = sum(results.values())

    if total == 0:
        st.info("No votes yet! Be the first to vote 👆")
    else:
        colors = ["🔵", "🔴", "🟢"]
        for i, (cname, votes) in enumerate(results.items()):
            percentage = (votes / total * 100) if total > 0 else 0
            st.markdown(f"**{colors[i]} {cname}**")
            st.progress(percentage / 100)
            st.caption(f"{votes} vote(s) — {percentage:.1f}%")
            st.markdown("")

        winner = max(results, key=results.get)
        st.markdown("---")
        st.markdown("### 🏆 Current Leader")
        st.success(f"**{winner}** is leading with **{results[winner]}** vote(s)!")

    st.markdown("---")
    st.markdown("### 💡 Why Aadhaar as Primary Key?")
    st.markdown("""
    - 🪪 **Unique Identity** — No two people share an Aadhaar
    - 🚫 **Prevents Fraud** — Same ID can't vote twice
    - 🔒 **Privacy Protected** — Only last 4 digits shown
    - ✅ **Government Verified** — Real-world authenticity
    - 🔗 **Part of Hash** — ID is baked into the block's fingerprint
    """)

    st.markdown("### 🔗 How Blockchain Protects Votes")
    st.markdown("""
    - Each vote = one immutable block
    - SHA-256 hash = unique fingerprint
    - Any change breaks the entire chain
    - No central authority can alter results
    """)

# ------ COLUMN 3: BLOCKCHAIN EXPLORER ------
with col3:
    st.markdown('<div class="section-title">🔍 Blockchain Explorer</div>', unsafe_allow_html=True)
    st.caption("All blocks in the chain ↓")

    for block in bc.get_chain_data():
        if block["Block #"] == 0:
            st.markdown(f"""
            <div class="genesis-card">
                <b>⭐ Block #0 — GENESIS</b><br>
                📅 {block['Time'][:19]}<br>
                🔑 Hash: <code>{block['Hash']}</code>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="block-card">
                <b>🧱 Block #{block['Block #']}</b><br>
                👤 Name: {block['Voter Name']}<br>
                🪪 ID: <code>{block['Voter ID (Masked)']}</code><br>
                🗳️ Voted: {block['Voted For']}<br>
                📅 {block['Time'][:19]}<br>
                🔑 Hash: <code>{block['Hash']}</code><br>
                🔗 Prev: <code>{block['Previous Hash']}</code>
            </div>
            """, unsafe_allow_html=True)

# Bottom section
st.markdown("---")
with st.expander("📚 About This Project — What is Blockchain? (Click to expand)"):
    st.markdown("""
    ## 🔗 What is Blockchain?
    A **Blockchain** is a special database where data is stored in **blocks** chained together.
    Once added, data **cannot be changed** — perfect for voting!

    ### Key Concepts in This Project:
    | Concept | Explanation |
    |---|---|
    | **Block** | Holds one vote + Aadhaar + timestamp + hash |
    | **Primary Key** | Aadhaar / Voter ID — uniquely identifies each voter |
    | **Hash (SHA-256)** | Unique fingerprint of block data |
    | **Genesis Block** | Block #0, starts the chain |
    | **Immutability** | Changing any vote breaks the hash chain |
    | **Masking** | Aadhaar last 4 digits shown for privacy |

    ### Why Aadhaar as Primary Key?
    In databases, a **Primary Key** is a unique identifier for each record.
    In our blockchain, we use Aadhaar/Voter ID as the primary key because:
    - It is government-issued and unique to every individual
    - It prevents the same person from voting twice
    - It is more reliable than a name (two people can have the same name!)

    ### Technologies Used:
    - **Python** — Core language
    - **Streamlit** — Web UI
    - **hashlib** — SHA-256 hashing
    - **Custom Blockchain** — Built from scratch
    """)

st.markdown("---")
st.markdown('<p style="text-align:center; color:#555; font-size:0.85rem;">BlockVote | Foundation of Blockchain — Micro Project | Aadhaar-Verified Voting System</p>', unsafe_allow_html=True)
