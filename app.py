import streamlit as st
import time
from blockchain import Blockchain
from database import cast_vote, get_all_votes, get_results, is_chain_valid, masked_id

st.set_page_config(
    page_title="BlockVote - Live Voting",
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
    .live-badge {
        display: inline-block;
        background: #ff4444;
        color: white;
        font-size: 0.75rem;
        font-weight: bold;
        padding: 3px 10px;
        border-radius: 20px;
        animation: pulse 1.5s infinite;
        margin-left: 8px;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
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
    .stat-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(0,210,255,0.2);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 8px 0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Blockchain logic (validation only, DB is source of truth) ──
bc = Blockchain()

# ── Auto-refresh every 5 seconds ──
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

# ── Header ──
st.markdown('<div class="main-title">🗳️ BlockVote</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Blockchain Voting System '
    '<span class="live-badge">● LIVE</span>'
    ' &nbsp;|&nbsp; Real-time • Aadhaar-Verified • Tamper-Proof</div>',
    unsafe_allow_html=True
)
st.markdown("---")

# ── Fetch live data from Supabase ──
all_votes = get_all_votes()
results = get_results(bc.candidates)
total_votes = len(all_votes)
chain_ok = is_chain_valid()

# ── Layout ──
col1, col2, col3 = st.columns([1.2, 1.2, 1])

# ────────────────────────────────────────────────────────────
# COLUMN 1 — CAST VOTE
# ────────────────────────────────────────────────────────────
with col1:
    st.markdown('<div class="section-title">📥 Cast Your Vote</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">🔒 Your Aadhaar / Voter ID is your unique key. Each ID can only vote once — forever.</div>', unsafe_allow_html=True)
    st.markdown('<div class="warning-box">🛡️ <b>Privacy:</b> Only last 4 digits of your ID are shown in the blockchain.</div>', unsafe_allow_html=True)

    voter_name = st.text_input("👤 Full Name", placeholder="e.g. Rahul Sharma")

    id_type_choice = st.radio(
        "🪪 ID Type",
        ["Aadhaar Number (12 digits)", "Voter ID (10 digits)"],
        horizontal=True
    )

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
            # Validate format first
            valid, result = bc.validate_vote_input(voter_name, voter_id, candidate)
            if not valid:
                st.error(result)
            else:
                # Save to Supabase (shared database)
                success, message = cast_vote(voter_name.strip(), voter_id.strip(), candidate)
                if success:
                    st.success(message)
                    st.balloons()
                    time.sleep(1)
                    st.rerun()  # Refresh page to show updated data
                else:
                    st.error(message)

    st.markdown("---")

    # Live stats
    st.markdown("### 📊 Live Stats")
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(f'<div class="stat-box"><div style="font-size:2rem;font-weight:900;color:#00d2ff;">{total_votes}</div><div style="color:#aaa;font-size:0.85rem;">Total Votes</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-box"><div style="font-size:2rem;font-weight:900;color:#7b2ff7;">{total_votes + 1}</div><div style="color:#aaa;font-size:0.85rem;">Blocks in Chain</div></div>', unsafe_allow_html=True)

    st.markdown("**Chain Integrity:**")
    if chain_ok:
        st.markdown('<span class="valid-badge">✅ CHAIN VALID</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="invalid-badge">❌ CHAIN TAMPERED!</span>', unsafe_allow_html=True)

    st.markdown("")
    if st.button("🔄 Refresh Results", use_container_width=True):
        st.rerun()


# ────────────────────────────────────────────────────────────
# COLUMN 2 — LIVE RESULTS
# ────────────────────────────────────────────────────────────
with col2:
    st.markdown(
        '<div class="section-title">📈 Live Results <span class="live-badge">● LIVE</span></div>',
        unsafe_allow_html=True
    )

    if total_votes == 0:
        st.info("No votes yet! Be the first to vote 👆")
    else:
        colors = ["🔵", "🔴", "🟢"]
        for i, (cname, votes) in enumerate(results.items()):
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            st.markdown(f"**{colors[i]} {cname}**")
            st.progress(percentage / 100)
            st.caption(f"{votes} vote(s) — {percentage:.1f}%")
            st.markdown("")

        winner = max(results, key=results.get)
        winner_votes = results[winner]
        st.markdown("---")
        st.markdown("### 🏆 Current Leader")
        st.success(f"**{winner}** is leading with **{winner_votes}** vote(s)!")

    st.markdown("---")
    st.markdown("### 🌐 How Real-Time Sync Works")
    st.markdown("""
    - 🗄️ **Supabase Database** — All votes stored in cloud
    - 🔄 **Every device** reads from the same database
    - ⚡ **Instant sync** — Vote on phone, see it on laptop
    - 🔒 **Double vote** blocked at database level too
    - ♾️ **Persistent** — Data stays even if app restarts
    - 🌍 **Global** — Works from anywhere in the world
    """)

    st.markdown("### 💡 Blockchain Concepts")
    st.markdown("""
    - Each vote = one immutable block
    - SHA-256 hash = unique fingerprint
    - Chain links = previous hash stored in each block
    - Aadhaar = primary key (unique per voter)
    """)


# ────────────────────────────────────────────────────────────
# COLUMN 3 — BLOCKCHAIN EXPLORER
# ────────────────────────────────────────────────────────────
with col3:
    st.markdown('<div class="section-title">🔍 Blockchain Explorer</div>', unsafe_allow_html=True)
    st.caption("All blocks stored in Supabase ↓")

    # Genesis block
    st.markdown(f"""
    <div class="genesis-card">
        <b>⭐ Block #0 — GENESIS</b><br>
        🔑 Hash: <code>000000...000000</code><br>
        📝 Chain origin block
    </div>
    """, unsafe_allow_html=True)

    # All vote blocks
    for i, vote in enumerate(all_votes):
        block_num = i + 1
        m_id = masked_id(vote["voter_id"])
        ts = str(vote["timestamp"])[:19]
        h = vote["block_hash"][:20] + "..."
        p = vote["previous_hash"][:20] + "..."

        st.markdown(f"""
        <div class="block-card">
            <b>🧱 Block #{block_num}</b><br>
            👤 {vote['voter_name']}<br>
            🪪 ID: <code>{m_id}</code><br>
            🗳️ {vote['candidate']}<br>
            📅 {ts}<br>
            🔑 <code>{h}</code><br>
            🔗 <code>{p}</code>
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# BOTTOM — AUTO REFRESH + ABOUT
# ────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📚 About This Project (Click to expand)"):
    st.markdown("""
    ## 🔗 BlockVote — Blockchain Voting System

    ### Architecture
    | Layer | Technology |
    |---|---|
    | **Frontend** | Streamlit (Python) |
    | **Blockchain Logic** | Custom Python (SHA-256) |
    | **Database** | Supabase (PostgreSQL) |
    | **Hosting** | Streamlit Cloud |
    | **Real-time Sync** | Supabase REST API |

    ### Key Concepts
    | Concept | Implementation |
    |---|---|
    | **Block** | Each vote = one DB record with hash |
    | **Primary Key** | Aadhaar / Voter ID (UNIQUE constraint) |
    | **Hashing** | SHA-256 on voter data + previous hash |
    | **Chain** | Each block stores previous block's hash |
    | **Immutability** | DB record + hash verification |
    | **Decentralization** | Cloud DB accessible from anywhere |
    | **Real-time** | All devices read same Supabase table |

    ### Why Supabase?
    Supabase provides a **PostgreSQL cloud database** that acts as the
    shared source of truth. Every device — phone, laptop, anywhere in the
    world — reads and writes to the same database, so all votes are
    instantly visible to everyone.
    """)

st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#555; font-size:0.85rem;">'
    'BlockVote | Foundation of Blockchain | Powered by Supabase + Streamlit Cloud'
    '</p>',
    unsafe_allow_html=True
)

# Auto-refresh every 5 seconds silently
time.sleep(5)
st.rerun()
