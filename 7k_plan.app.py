import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Guild Boss Planner", layout="wide")

# --- Initialize session state ---
if 'players' not in st.session_state:
    st.session_state.players = pd.DataFrame({
        'Name': [f'Player{i+1}' for i in range(5)],
        'Teo': [0]*5,
        'Kyle': [0]*5,
        'Yoonhee': [0]*5,
        'Karma': [0]*5
    })

# --- Sidebar / Inputs ---
st.sidebar.header("ตั้งค่า")
guild_name = st.sidebar.text_input("ชื่อกิลด์", value="MyGuild")
max_players = st.sidebar.number_input("จำนวนผู้เล่น (สูงสุด 30)", min_value=1, max_value=30, value=30)
hp_teo = st.sidebar.number_input("HP Teo", value=100_000_000)
hp_kyle = st.sidebar.number_input("HP Kyle", value=100_000_000)
hp_yoonhee = st.sidebar.number_input("HP Yoonhee", value=100_000_000)
hp_karma = st.sidebar.number_input("HP Karma", value=100_000_000)

# --- Players Table ---
st.subheader("ข้อมูลผู้เล่น")
df = st.experimental_data_editor(st.session_state.players, num_rows="dynamic", key="players_editor")
st.session_state.players = df.head(max_players)  # trim to max_players

# --- Helper to parse input like "1.5m" ---
def parse_damage(val):
    if isinstance(val, str):
        s = val.lower().replace(',', '').strip()
        if s.endswith('m'): return int(float(s[:-1])*1_000_000)
        if s.endswith('k'): return int(float(s[:-1])*1_000)
        return int(float(s))
    return int(val)

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
                # โจมตีบอสที่สามารถทำ damage มากที่สุด
                target = max(alive_bosses, key=lambda b: p[b])
                dmg = min(p[target], remaining[target])
                assigns.append({'Player': p['Name'], 'Boss': target, 'Damage': dmg})
                remaining[target] -= dmg
        result.append({'Day': day, 'Assignments': assigns, 'Remaining': remaining.copy()})
    return result

# --- Generate Button ---
if st.button("สร้างแผน (ปรับอัตโนมัติ)"):
    hp_dict = {'Teo': hp_teo, 'Kyle': hp_kyle, 'Yoonhee': hp_yoonhee, 'Karma': hp_karma}
    plan = generate_plan(st.session_state.players, hp_dict)
    st.session_state.last_plan = plan

# --- Display Plan ---
if 'last_plan' in st.session_state:
    st.subheader("ผลลัพธ์แผน")
    for day_info in st.session_state.last_plan:
        st.markdown(f"**Day {day_info['Day']}**")
        rem = day_info['Remaining']
        st.markdown(f"HP Left — Teo: {rem['Teo']:,} / Kyle: {rem['Kyle']:,} / Yoonhee: {rem['Yoonhee']:,} / Karma: {rem['Karma']:,}")
        for a in day_info['Assignments']:
            st.markdown(f"- {a['Player']} → {a['Boss']} : {a['Damage']:,}")

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
