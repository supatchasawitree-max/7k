import streamlit as st
import pandas as pd

st.set_page_config(page_title="ตัววางแผน Guild Boss Seven Knight")

st.markdown("<h3>ตัววางแผน Guild Boss Seven Knight</h3>", unsafe_allow_html=True)

# --- Inputs ---
guild_name = st.text_input("ชื่อกิลด์", "")
max_players = st.number_input("จำนวนผู้เล่น (สูงสุด 30)", min_value=1, max_value=30, value=30)
default_hp = st.number_input("HP ของบอสเริ่มต้น", value=100_000_000)

st.markdown("### ผู้เล่น (ชื่อ | Teo | Kyle | Yoonhee | Karma)")

# --- Table ---
if "players" not in st.session_state:
    # สร้าง table เริ่มต้น 5 คน
    st.session_state.players = pd.DataFrame({
        "ชื่อ": [f"Player{i+1}" for i in range(5)],
        "Teo": [0]*5,
        "Kyle": [0]*5,
        "Yoonhee": [0]*5,
        "Karma": [0]*5
    })

# เพิ่มผู้เล่น
if st.button("+ เพิ่มผู้เล่น"):
    if len(st.session_state.players) < max_players:
        st.session_state.players.loc[len(st.session_state.players)] = [f"Player{len(st.session_state.players)+1}",0,0,0,0]

# ลบผู้เล่น
def remove_player(index):
    st.session_state.players.drop(index, inplace=True)
    st.session_state.players.reset_index(drop=True, inplace=True)

for i in range(len(st.session_state.players)):
    cols = st.columns([3,1,1,1,1,1])
    cols[0].text_input("ชื่อ", key=f"name_{i}", value=st.session_state.players.at[i,"ชื่อ"])
    cols[1].number_input("Teo", key=f"teo_{i}", value=st.session_state.players.at[i,"Teo"])
    cols[2].number_input("Kyle", key=f"kyle_{i}", value=st.session_state.players.at[i,"Kyle"])
    cols[3].number_input("Yoonhee", key=f"yoonhee_{i}", value=st.session_state.players.at[i,"Yoonhee"])
    cols[4].number_input("Karma", key=f"karma_{i}", value=st.session_state.players.at[i,"Karma"])
    if cols[5].button("ลบ", key=f"del_{i}"):
        remove_player(i)
        st.experimental_rerun()

# อัพเดตค่าใน DataFrame
for i in range(len(st.session_state.players)):
    st.session_state.players.at[i,"ชื่อ"] = st.session_state[f"name_{i}"]
    st.session_state.players.at[i,"Teo"] = st.session_state[f"teo_{i}"]
    st.session_state.players.at[i,"Kyle"] = st.session_state[f"kyle_{i}"]
    st.session_state.players.at[i,"Yoonhee"] = st.session_state[f"yoonhee_{i}"]
    st.session_state.players.at[i,"Karma"] = st.session_state[f"karma_{i}"]

# --- Boss HP ---
st.markdown("### HP บอส")
hp_teo = st.number_input("HP Teo", value=100_000_000)
hp_kyle = st.number_input("HP Kyle", value=100_000_000)
hp_yoonhee = st.number_input("HP Yoonhee", value=100_000_000)
hp_karma = st.number_input("HP Karma", value=100_000_000)

# --- Generate Plan ---
if st.button("สร้างแผน"):
    players = st.session_state.players.copy()
    remaining = {"Teo": hp_teo, "Kyle": hp_kyle, "Yoonhee": hp_yoonhee, "Karma": hp_karma}
    bosses = ["Teo", "Kyle", "Yoonhee", "Karma"]
    result = []
    day = 0

    while any(v>0 for v in remaining.values()) and day < 500:
        day += 1
        assigns = []
        for idx, p in players.iterrows():
            target_boss = min(bosses, key=lambda b: remaining[b])  # Assign to boss with lowest remaining
            dmg = min(p[target_boss], remaining[target_boss])
            assigns.append({"player": p["ชื่อ"], "boss": target_boss, "damage": dmg})
            remaining[target_boss] -= dmg
        snapshot = remaining.copy()
        result.append({"day": day, "assigns": assigns, "snapshot": snapshot})

    # แสดงผล
    for r in result:
        st.markdown(f"**Day {r['day']}**")
        st.text(f"HP Left — Teo: {r['snapshot']['Teo']:,} / Kyle: {r['snapshot']['Kyle']:,} / Yoonhee: {r['snapshot']['Yoonhee']:,} / Karma: {r['snapshot']['Karma']:,}")
        for a in r["assigns"]:
            st.text(f"{a['player']} → {a['boss']}: {a['damage']:,}")

# --- Export ---
st.download_button("ส่งออก CSV", data=st.session_state.players.to_csv(index=False), file_name=f"{guild_name}.csv")
st.download_button("ส่งออก XLSX", data=st.session_state.players.to_excel(index=False, engine='openpyxl'), file_name=f"{guild_name}.xlsx")
