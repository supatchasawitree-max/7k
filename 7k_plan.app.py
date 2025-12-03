import streamlit as st
import pandas as pd
import numpy as np
import io
import requests

st.set_page_config(page_title="ตัวช่วยวางแผนกิลด์บอส Seven Knights", layout="wide")

# ---------------------------
# Helper Functions
# ---------------------------

def parse_damage(val: str):
    if not val:
        return 0
    s = str(val).lower().replace(",", "").strip()
    if s.endswith("m"):
        return int(float(s[:-1]) * 1_000_000)
    if s.endswith("k"):
        return int(float(s[:-1]) * 1_000)
    try:
        return int(float(s))
    except:
        return 0

def fmt_m(num):
    return f"{num/1e6:.2f}M"

# ---------------------------
# UI - Initial Data
# ---------------------------

st.title("📘 ตัวช่วยวางแผนกิลด์บอส Seven Knights (เวอร์ชัน Streamlit)")
st.markdown("เครดิตคุณ Zero")

default_players = pd.DataFrame({
    "ชื่อผู้เล่น": [f"ผู้เล่น{i+1}" for i in range(5)],
    "เทโอ": ["" for _ in range(5)],
    "ไคล์": ["" for _ in range(5)],
    "ยอนฮี": ["" for _ in range(5)],
    "คาร์ม่า": ["" for _ in range(5)],
})

if "players" not in st.session_state:
    st.session_state.players = default_players.copy()

# ---------------------------
# Sidebar - Boss HP
# ---------------------------

st.sidebar.header("⚔️ ตั้งค่า HP บอส")
hp_teo = st.sidebar.number_input("HP เทโอ", value=100_000_000)
hp_kyle = st.sidebar.number_input("HP ไคล์", value=100_000_000)
hp_yh = st.sidebar.number_input("HP ยอนฮี", value=100_000_000)
hp_karma = st.sidebar.number_input("HP คาร์ม่า", value=100_000_000)

# ---------------------------
# Import Section
# ---------------------------

st.subheader("📥 นำเข้าข้อมูลผู้เล่น")

col1, col2, col3, col4 = st.columns(4)

# Import CSV/XLSX
uploaded = col1.file_uploader("นำเข้า CSV / XLSX", type=["csv", "xlsx"])
if uploaded:
    if uploaded.name.endswith(".csv"):
        st.session_state.players = pd.read_csv(uploaded)
    else:
        st.session_state.players = pd.read_excel(uploaded)
    st.success("นำเข้าข้อมูลสำเร็จ")

# Paste Clipboard
if col2.button("วางข้อมูล (Paste)"):
    try:
        text = st.text_area("วางข้อมูลที่นี่ (Name, Teo, Kyle, Yoonhee, Karma)")
        if text:
            df = pd.read_csv(io.StringIO(text), header=None)
            df.columns = ["ชื่อผู้เล่น", "เทโอ", "ไคล์", "ยอนฮี", "คาร์ม่า"]
            st.session_state.players = df
    except:
        st.error("ข้อมูลไม่ถูกต้อง")

# Google Sheet
if col3.button("นำเข้า Google Sheet (ลิงก์)"):
    url = st.text_input("วางลิงก์ Google Sheet ที่ตั้งเป็นสาธารณะ")
    if url:
        try:
            # Convert sheet URL to CSV
            if "spreadsheets" in url:
                base = url.split("/edit")[0]
                csv_url = base.replace("/edit", "") + "/export?format=csv"
                df = pd.read_csv(csv_url)
                st.session_state.players = df
                st.success("นำเข้าจาก Google Sheet สำเร็จ!")
        except:
            st.error("ลิงก์ไม่ถูกต้องหรือไม่ได้ตั้งค่าเป็นสาธารณะ")

# Reset
if col4.button("ล้างข้อมูลทั้งหมด"):
    st.session_state.players = default_players.copy()

# ---------------------------
# Editable Player Table
# ---------------------------

st.subheader("📝 ตารางผู้เล่น (แก้ไขได้)")
players_df = st.data_editor(
    st.session_state.players,
    num_rows="dynamic",
    use_container_width=True
)
st.session_state.players = players_df

# ---------------------------
# Generate the Plan
# ---------------------------

st.subheader("⚙️ สร้างแผนการตี (Auto-Optimize)")

if st.button("สร้างแผน"):
    players = []

    # Convert DataFrame → List of dicts
    for idx, r in players_df.iterrows():
        players.append({
            "name": r["ชื่อผู้เล่น"],
            "teo": parse_damage(r["เทโอ"]),
            "kyle": parse_damage(r["ไคล์"]),
            "yoonhee": parse_damage(r["ยอนฮี"]),
            "karma": parse_damage(r["คาร์ม่า"]),
        })

    bosses = ["teo", "kyle", "yoonhee", "karma"]
    hp = {
        "teo": hp_teo,
        "kyle": hp_kyle,
        "yoonhee": hp_yh,
        "karma": hp_karma
    }
    remaining = hp.copy()

    result = []
    day = 0

    # Main optimization loop (same logic as original)
    while any(v > 0 for v in remaining.values()) and day < 500:
        day += 1
        order = sorted(players, key=lambda p: max(p.values()), reverse=True)
        assigns = []

        for p in order:
            best_boss = None
            best_dmg = 0
            for b in bosses:
                if remaining[b] > 0 and p[b] > best_dmg:
                    best_dmg = p[b]
                    best_boss = b
            if best_boss:
                assigns.append({
                    "player": p["name"],
                    "boss": best_boss,
                    "damage": best_dmg
                })
                remaining[best_boss] = max(0, remaining[best_boss] - best_dmg)

        result.append({
            "day": day,
            "assigns": assigns,
            "remaining": remaining.copy()
        })

    st.session_state.result_plan = result
    st.success("สร้างแผนสำเร็จ!")

# ---------------------------
# Output Section
# ---------------------------

if "result_plan" in st.session_state:

    st.subheader("📊 ผลลัพธ์การวางแผน")

    for r in st.session_state.result_plan:
        st.markdown(f"### 📅 วันที่ {r['day']}")
        st.markdown(
            f"**HP คงเหลือ:** เทโอ: {r['remaining']['teo']:,} — "
            f"ไคล์: {r['remaining']['kyle']:,} — "
            f"ยอนฮี: {r['remaining']['yoonhee']:,} — "
            f"คาร์ม่า: {r['remaining']['karma']:,}"
        )

        df = pd.DataFrame([{
            "ผู้เล่น": a["player"],
            "บอส": a["boss"].upper(),
            "ดาเมจ": a["damage"],
            "ดาเมจ (M)": fmt_m(a["damage"])
        } for a in r["assigns"]])

        st.table(df)

    # Export CSV
    st.subheader("📤 ส่งออกผลลัพธ์")

    if st.button("ดาวน์โหลด CSV"):
        csv_buffer = io.StringIO()
        rows = []
        for d in st.session_state.result_plan:
            for a in d["assigns"]:
                rows.append([d["day"], a["player"], a["boss"], a["damage"]])
        df = pd.DataFrame(rows, columns=["วัน", "ผู้เล่น", "บอส", "ดาเมจ"])
        df.to_csv(csv_buffer, index=False)
        st.download_button("ดาวน์โหลด", csv_buffer.getvalue(), "plan.csv")

    # Export XLSX
    if st.button("ดาวน์โหลด XLSX"):
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("ดาวน์โหลด", buffer.getvalue(), "plan.xlsx")

    # Copy Markdown
    if st.button("คัดลอก Markdown"):
        md = "# แผนการตี\n\n"
        for d in st.session_state.result_plan:
            md += f"### วันที่ {d['day']}\n"
            for a in d["assigns"]:
                md += f"- {a['player']} → {a['boss'].upper()} ({fmt_m(a['damage'])})\n"
            md += "\n"
        st.code(md)

