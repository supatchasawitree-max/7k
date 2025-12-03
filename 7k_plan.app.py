import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Guild Boss Planner", layout="wide")

# --- Initialize session state ---
if 'players' not in st.session_state or not isinstance(st.session_state.players, pd.DataFrame):
    st.session_state.players = pd.DataFrame({
        'Name': [f'Player{i+1}' for i in range(5)],
        'Teo': [0]*5,
        'Kyle': [0]*5,
        'Yoonhee': [0]*5,
        'Karma': [0]*5
    })

if 'last_plan' not in st.session_state:
    st.session_state.last_plan = []

# --- Sidebar / Inputs ---
st.sidebar.header("ตั้งค่า")
guild_name = st.sidebar.text_input("ชื่อกิลด์", value="MyGuild")
max_players = st.sidebar.number_input("จำนวนผู้เล่น (สูงสุด 30)", min_value=1, max_value=30, value=30)
hp_teo = st.sidebar.number_input("HP Teo", value=100_000_000)
hp_kyle = st.sidebar.number_input("HP Kyle", value=100_000_000)
hp_yoonhee = st.sidebar.number_input("HP Yoonhee", value=100_000_000)
hp_karma = st.sidebar.number_input("HP Karma", value=100_000_000)

# --- Helpers ---
def parse_damage(val):
    if isinstance(val, str):
        s = val.lower().replace(',', '').strip()
        if s.endswith('m'): return int(float(s[:-1])*1_000_000)
        if s.endswith('k'): return int(float(s[:-1])*1_000)
        return int(float(s))
    try:
        return int(val)
    except:
        return 0

def fmtM(n):
    return f"{n/1_000_000:.3f}".rstrip('0').rstrip('.') + 'M'

# --- Players Table ---
st.subheader("ข้อมูลผู้เล่น")
players_df = st.session_state.players.copy()

# ให้ผู้ใช้แก้ไข
edited_df = st.data_editor(
    players_df, 
    num_rows="dynamic",
    use_container_width=True
)

# Update session state
st.session_state.players = edited_df.head(max_players)

# ปุ่มเพิ่มผู้เล่น
if st.button("เพิ่มผู้เล่น"):
    new_player = pd.DataFrame({'Name':[f'Player{len(st.session_state.players)+1}'],
                               'Teo':[0],'Kyle':[0],'Yoonhee':[0],'Karma':[0]})
    st.session_state.players = pd.concat([st.session_state.players, new_player], ignore_index=True)

# ปุ่มลบผู้เล่นแถวสุดท้าย
if st.button("ลบผู้เล่นล่าสุด"):
    if len(st.session_state.players) > 0:
        st.session_state.players = st.session_state.players.iloc[:-1]

# --- Generate Plan ---
def generate_plan(players_df, hp_dict):
    bosses = ['Teo', 'Kyle', 'Yoonhee', 'Karma']
    result = []
    remaining = hp_dict.copy()
    day = 0
    players = []
    for _, row in players_df.iterrows():
        players.append({
            'Name': row['Name'],
            'Teo': parse_damage(row['Teo']),
            'Kyle': parse_damage(row['Kyle']),
            'Yoonhee': parse_damage(row['Yoonhee']),
            'Karma': parse_damage(row['Karma'])
        })

    while any(v>0 for v in remaining.values()) and day < 500:
        day += 1
        assigns = []
        for p in players:
            alive_bosses = [b for b in bosses if remaining[b] > 0]
            if alive_bosses:
                # เลือกบอสที่ผู้เล่นทำ Damage สูงสุด
                target = max(alive_bosses, key=lambda b: p[b])
                dmg = min(p[target], remaining[target])
                assigns.append({'Player': p['Name'], 'Boss': target, 'Damage': dmg})
                remaining[target] -= dmg
        result.append({'Day': day, 'Assignments': assigns, 'Remaining': remaining.copy()})
    return result

if st.button("สร้างแผน (ปรับอัตโนมัติ)"):
    hp_dict = {'Teo': hp_teo, 'Kyle': hp_kyle, 'Yoonhee': hp_yoonhee, 'Karma': hp_karma}
    st.session_state.last_plan = generate_plan(st.session_state.players, hp_dict)

# --- Display Plan ---
if st.session_state.last_plan:
    st.subheader("ผลลัพธ์แผน")
    for day_info in st.session_state.last_plan:
        st.markdown(f"**Day {day_info['Day']}**")
        rem = day_info['Remaining']
        st.markdown(f"HP Left — Teo: {rem['Teo']:,} / Kyle: {rem['Kyle']:,} / Yoonhee: {rem['Yoonhee']:,} / Karma: {rem['Karma']:,}")
        for a in day_info['Assignments']:
            st.markdown(f"- {a['Player']} → {a['Boss']} : {a['Damage']:,} ({fmtM(a['Damage'])})")

# --- Export CSV/XLSX ---
col1, col2 = st.columns(2)
with col1:
    csv_data = st.session_state.players.to_csv(index=False).encode('utf-8')
    st.download_button("ส่งออก CSV", data=csv_data, file_name=f"{guild_name}.csv", mime="text/csv")
with col2:
    output = io.BytesIO()
    st.session_state.players.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        "ส่งออก XLSX",
        data=output,
        file_name=f"{guild_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
