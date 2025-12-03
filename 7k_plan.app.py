import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ตัววางแผน Guild Boss Seven Knight", layout="wide")

st.title("ตัววางแผน Guild Boss Seven Knight")

# -----------------------------
# Session state สำหรับผู้เล่น
# -----------------------------
if "players" not in st.session_state:
    st.session_state.players = pd.DataFrame(
        columns=["Name", "Teo", "Kyle", "Yoonhee", "Karma"]
    )

# -----------------------------
# ข้อมูลผู้เล่น
# -----------------------------
st.subheader("ข้อมูลผู้เล่น")
st.session_state.players = st.data_editor(
    st.session_state.players,
    num_rows="dynamic",
    key="players_editor"
)

# ปุ่มล้างข้อมูล
if st.button("ล้างข้อมูลทั้งหมด"):
    st.session_state.players = pd.DataFrame(
        columns=["Name", "Teo", "Kyle", "Yoonhee", "Karma"]
    )
    st.experimental_rerun()

# -----------------------------
# ข้อมูล HP ของบอส
# -----------------------------
st.subheader("HP ของบอส")
col1, col2, col3, col4 = st.columns(4)
with col1:
    hp_teo = st.number_input("HP Teo", value=100_000_000)
with col2:
    hp_kyle = st.number_input("HP Kyle", value=100_000_000)
with col3:
    hp_yoonhee = st.number_input("HP Yoonhee", value=100_000_000)
with col4:
    hp_karma = st.number_input("HP Karma", value=100_000_000)

# -----------------------------
# ฟังก์ชันแปลงค่า
# -----------------------------
def parse_damage(val):
    if not val:
        return 0
    s = str(val).strip().lower().replace(",", "")
    if s.endswith("m"):
        return int(float(s[:-1]) * 1_000_000)
    if s.endswith("k"):
        return int(float(s[:-1]) * 1_000)
    return int(float(s))

def fmt_m(n):
    return f"{n/1_000_000:.3f}M".rstrip("0").rstrip(".")

# -----------------------------
# สร้างแผนต่อบอส
# -----------------------------
if st.button("สร้างแผน (ปรับอัตโนมัติ)"):
    players = st.session_state.players.copy()
    # แปลงค่าเป็นตัวเลข
    for boss in ["Teo", "Kyle", "Yoonhee", "Karma"]:
        players[boss] = players[boss].apply(parse_damage)

    remaining = {
        "Teo": hp_teo,
        "Kyle": hp_kyle,
        "Yoonhee": hp_yoonhee,
        "Karma": hp_karma,
    }

    bosses = ["Teo", "Kyle", "Yoonhee", "Karma"]
    result = []
    day = 0

    while any(v > 0 for v in remaining.values()) and day < 500:
        day += 1
        assigns = []
        for _, p in players.iterrows():
            # เลือก boss ที่ยังเหลือ HP และที่ทำ dmg สูงสุด
            available = [b for b in bosses if remaining[b] > 0]
            if not available:
                continue
            target = max(available, key=lambda b: p[b])
            dmg = min(p[target], remaining[target])
            assigns.append({"player": p["Name"], "boss": target, "damage": dmg})
            remaining[target] -= dmg
        result.append({"day": day, "assigns": assigns, "snapshot": remaining.copy()})

    # แสดงผล
    for r in result:
        st.markdown(f"**Day {r['day']}**")
        st.markdown(
            f"HP Left — Teo: {r['snapshot']['Teo']:,} / Kyle: {r['snapshot']['Kyle']:,} "
            f"/ Yoonhee: {r['snapshot']['Yoonhee']:,} / Karma: {r['snapshot']['Karma']:,}"
        )
        for a in r["assigns"]:
            st.markdown(f"- {a['player']} → {a['boss']} • {a['damage']:,} ({fmt_m(a['damage'])})")
        st.markdown("---")

# -----------------------------
# ส่งออก CSV / XLSX
# -----------------------------
st.subheader("ส่งออกข้อมูล")
guild_name = st.text_input("ชื่อกิลด์ (สำหรับไฟล์)", "Guild")

# CSV
csv_data = st.session_state.players.to_csv(index=False).encode("utf-8")
st.download_button("ส่งออก CSV", data=csv_data, file_name=f"{guild_name}.csv", mime="text/csv")

# XLSX
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    st.session_state.players.to_excel(writer, index=False, sheet_name="Players")
    writer.save()
st.download_button("ส่งออก XLSX", data=output.getvalue(), file_name=f"{guild_name}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
