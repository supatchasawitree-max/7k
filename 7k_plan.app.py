import streamlit as st
import pandas as pd
import io

st.title("ตัววางแผน Guild Boss Seven Knight")

# กำหนด session_state สำหรับผู้เล่น
if "players" not in st.session_state:
    st.session_state.players = pd.DataFrame(columns=["Name","Teo","Kyle","Yoonhee","Karma"])

# แก้ไขข้อมูลผู้เล่น
st.subheader("ข้อมูลผู้เล่น")
st.session_state.players = st.experimental_data_editor(
    st.session_state.players, 
    num_rows="dynamic",
    key="players_editor"
)

# กำหนด HP ของบอส
st.subheader("HP ของบอส")
hp_teo = st.number_input("HP Teo", value=100_000_000)
hp_kyle = st.number_input("HP Kyle", value=100_000_000)
hp_yoonhee = st.number_input("HP Yoonhee", value=100_000_000)
hp_karma = st.number_input("HP Karma", value=100_000_000)

# ปุ่มล้างข้อมูล
if st.button("ล้างข้อมูลทั้งหมด"):
    st.session_state.players = pd.DataFrame(columns=["Name","Teo","Kyle","Yoonhee","Karma"])
    st.experimental_rerun()

# ปุ่มสร้างแผน (คำนวณ)
if st.button("สร้างแผน"):
    # แปลงค่าเป็นตัวเลข
    df = st.session_state.players.copy()
    for col in ["Teo","Kyle","Yoonhee","Karma"]:
        df[col] = pd.to_numeric(df[col].replace({r'[mk]': ''}, regex=True), errors='coerce').fillna(0)
        # คูณค่า m/k
        df[col] = df[col].apply(lambda x: x*1_000_000 if 'm' in str(x).lower() else x)
        df[col] = df[col].apply(lambda x: x*1_000 if 'k' in str(x).lower() else x)
    
    # HP ของบอส
    remaining = {"Teo": hp_teo, "Kyle": hp_kyle, "Yoonhee": hp_yoonhee, "Karma": hp_karma}
    bosses = ["Teo","Kyle","Yoonhee","Karma"]
    result = []
    day = 0

    while any(v>0 for v in remaining.values()) and day<500:
        day += 1
        assigns = []
        for idx, row in df.iterrows():
            # เลือกบอสที่ HP >0
            alive = [b for b in bosses if remaining[b] > 0]
            if not alive:
                continue
            # เลือกบอสที่ผู้เล่นทำ damage สูงสุด
            target = max(alive, key=lambda b: row[b])
            dmg = min(row[target], remaining[target])
            remaining[target] -= dmg
            assigns.append(f"{row['Name']} → {target}: {dmg:,}")
        result.append((day, assigns, remaining.copy()))

    # แสดงผล
    for day, assigns, snapshot in result:
        st.markdown(f"**Day {day}**")
        st.markdown("HP Left — " + " / ".join([f"{k}: {v:,}" for k,v in snapshot.items()]))
        for a in assigns:
            st.markdown(f"- {a}")

# ส่งออก CSV
st.subheader("ส่งออกข้อมูล")
guild_name = st.text_input("ชื่อกิลด์ (สำหรับไฟล์)", "Guild")
csv_data = st.session_state.players.to_csv(index=False).encode("utf-8")
st.download_button("ส่งออก CSV", data=csv_data, file_name=f"{guild_name}.csv", mime="text/csv")
