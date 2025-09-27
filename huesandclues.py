import streamlit as st
import random
import math

# Hues & Cues simplified implementation for Streamlit
# Local multiplayer: Host picks a secret color, gives a cue, players guess.

st.set_page_config(page_title="Hues & Cues Online", layout="wide")

# --- Session state init ---
if "size" not in st.session_state:
    st.session_state.size = 6
    st.session_state.colors = []
    st.session_state.secret_index = None
    st.session_state.cue = ""
    st.session_state.players = ["Alice", "Bob"]
    st.session_state.scores = [0, 0]
    st.session_state.guesses = []
    st.session_state.round = 1
    st.session_state.current_player_idx = 0
    st.session_state.host_mode = True

# --- Helpers ---
def generate_colors(n):
    arr = []
    for r in range(n):
        for c in range(n):
            hue = round((r * n + c) * (360 / (n * n)))
            sat = round(40 + (c / (n - 1 or 1)) * 50)
            lig = round(30 + (r / (n - 1 or 1)) * 50)
            arr.append(f"hsl({hue}, {sat}%, {lig}%)")
    st.session_state.colors = arr
    st.session_state.secret_index = None
    st.session_state.cue = ""
    st.session_state.guesses = []

def coords_from(index, size):
    return dict(r=index // size, c=index % size)

def distance(aIdx, bIdx, size):
    a, b = coords_from(aIdx, size), coords_from(bIdx, size)
    return math.hypot(a['r'] - b['r'], a['c'] - b['c'])

# --- UI ---
st.title("🎨 Hues & Cues — Streamlit Edition")
st.caption("Local multiplayer: host picks a color and gives a clue, players guess on the grid.")

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Game Board")
    size = st.selectbox("Grid size", [4,5,6,7,8], index=2, key="size")
    if st.button("Generate colors"):
        generate_colors(size)
    if not st.session_state.colors:
        generate_colors(size)

    # Render grid
    for r in range(size):
        cols = st.columns(size)
        for c in range(size):
            idx = r*size+c
            col = st.session_state.colors[idx]
            label = ""
            if st.session_state.secret_index == idx and not st.session_state.host_mode:
                label = "SECRET"
            if cols[c].button(label or " ", key=f"cell-{idx}", help=f"Cell {idx}", use_container_width=True):
                if st.session_state.host_mode:
                    st.session_state.secret_index = idx
                else:
                    secret = st.session_state.secret_index
                    if secret is None:
                        st.warning("Host hasn't picked a secret yet.")
                    else:
                        dist = distance(idx, secret, size)
                        points = max(0, round(size*2+2 - dist*2))
                        p = st.session_state.current_player_idx
                        st.session_state.guesses.append({
                            "player": st.session_state.players[p],
                            "index": idx,
                            "dist": dist
                        })
                        st.session_state.scores[p] += points
                        st.session_state.current_player_idx = (p+1) % len(st.session_state.players)
            cols[c].markdown(f'<div style="background:{col};width:100%;padding-top:100%;border-radius:6px"></div>', unsafe_allow_html=True)

    st.text_input("Cue", key="cue", disabled=not st.session_state.host_mode)
    if st.button("Start Round", disabled=not st.session_state.host_mode):
        if st.session_state.secret_index is None:
            st.warning("Host must pick a secret color first.")
        elif not st.session_state.cue.strip():
            st.warning("Host must type a short cue.")
        else:
            st.session_state.host_mode = False

    c1, c2, c3 = st.columns(3)
    if c1.button("Reveal"):
        st.session_state.host_mode = False
    if c2.button("Next Round"):
        st.session_state.round += 1
        st.session_state.host_mode = True
        st.session_state.secret_index = None
        st.session_state.cue = ""
        st.session_state.guesses = []
        st.session_state.current_player_idx = 0
    if c3.button("Reset Game"):
        st.session_state.scores = [0]*len(st.session_state.players)
        st.session_state.round = 1
        st.session_state.secret_index = None
        st.session_state.cue = ""
        st.session_state.guesses = []
        st.session_state.host_mode = True

    st.subheader("Clue")
    st.write(st.session_state.cue or "(No cue yet)")

    st.subheader("Guesses")
    if not st.session_state.guesses:
        st.caption("No guesses yet")
    else:
        for g in st.session_state.guesses:
            st.write(f"{g['player']} → Cell {g['index']} (dist {g['dist']:.2f})")

with col2:
    st.subheader("Players & Scores")
    for i, p in enumerate(st.session_state.players):
        cols = st.columns([3,1,1])
        name = cols[0].text_input(f"Player {i+1}", value=p, key=f"player-{i}")
        st.session_state.players[i] = name
        cols[1].write(st.session_state.scores[i])
        if cols[2].button("❌", key=f"rem-{i}"):
            st.session_state.players.pop(i)
            st.session_state.scores.pop(i)
            st.experimental_rerun()
    if st.button("Add Player"):
        st.session_state.players.append(f"Player {len(st.session_state.players)+1}")
        st.session_state.scores.append(0)

    st.write("**Current turn:**", st.session_state.players[st.session_state.current_player_idx] if st.session_state.players else "—", "(host picks)" if st.session_state.host_mode else "(to guess)")

st.markdown("---")
st.caption("Tip: Host secretly chooses a color and provides a short cue. Players take turns clicking the grid to guess.")
