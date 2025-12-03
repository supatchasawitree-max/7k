# app.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="ตัววางแผนกิลด์บอส Seven Knights", layout="wide")

st.title("ตัววางแผนกิลด์บอส Seven Knights")
st.markdown("HTML แบบ Standalone — นำเข้าจาก Google Sheet (สาธารณะ), CSV/XLSX หรือวางข้อมูล — ไม่ต้องล็อกอิน")

# --- ข้อมูลพื้นฐาน ---
guild_name = st.text_input("ชื่อกิลด์", "")
max_players = st.number_input("จำนวนผู้เล่น (สูงสุด 30)", min_value=1, max_value=30, value=30)
default_hp = st.number_input("ค่า HP บอสเริ่มต้น (Default)", value=100_000_000)

# --- HP ของบอส ---
st.subheader("ค่า HP ของบอส")
col1, col2, col3, col4 = st.columns(4)
hp_teo = col1.number_input("HP เทโอ", value=default_hp)
hp_kyle = col2.number_input("HP ไคล์", value=default_hp)
hp_yoonhee = col3.number_input("HP ยอนฮี", value=default_hp)
hp_karma = col4.number_input("HP คาร์ม่า", value=default_hp)

# --- ฟังก์ชันช่วยแปลงค่า ---
def parse_damage(val):
    if pd.isna(val) or val=="":
        return 0
    val = str(val).lower().replace(",","")
    if val.endswith("m"):
        return int(float(val[:-1])*1_000_000)
    if val.endswith("k"):
        return int(float(val[:-1])*1_000)
    return int(float(val))

def fmtM(n):
    return f"{n/1_000_000:.3f}".rstrip("0").rstrip(".") + "M"

# --- โหลด/สร้าง DataFrame ผู้เล่น ---
if "players" not in st.session_state:
    st.session_state.players = pd.DataFrame(
        columns=["ชื่อ", "เทโอ", "ไคล์", "ยอนฮี", "คาร์ม่า"]
    )

# --- นำเข้าข้อมูล CSV/XLSX ---
st.subheader("นำเข้าข้อมูล")
uploaded_file = st.file_uploader("นำเข้า CSV/XLSX", type=["csv","xlsx"])
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        df = df.rename(columns={df.columns[0]:"ชื่อ"})  # แก้ชื่อคอลัมน์แรกเป็น "ชื่อ"
        st.session_state.players = df[["ชื่อ","เทโอ","ไคล์","ยอนฮี","คาร์ม่า"]]
        st.success(f"นำเข้าข้อมูล {len(df)} แถวสำเร็จ")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

# --- แก้ไขตารางผู้เล่น ---
st.subheader("รายชื่อผู้เล่น")
st.session_state.players = st.data_editor(
    st.session_state.players,
    num_rows="dynamic",
    use_container_width=True
)

# --- สร้างแผน Auto Optimize ---
if st.button("สร้างแผนอัตโนมัติ"):
    players = st.session_state.players.copy()
    for boss in ["เทโอ","ไคล์","ยอนฮี","คาร์ม่า"]:
        players[boss] = players[boss].apply(parse_damage)
    remaining = {"เทโอ": hp_teo, "ไคล์": hp_kyle, "ยอนฮี": hp_yoonhee, "คาร์ม่า": hp_karma}
    result = []
    day = 0
    bosses = ["เทโอ","ไคล์","ยอนฮี","คาร์ม่า"]
    
    while any(v>0 for v in remaining.values()) and day<500:
        day += 1
        order = players.copy()
        order["max_dmg"] = order[bosses].max(axis=1)
        order = order.sort_values(by="max_dmg", ascending=False)
        assigns = []
        for idx, p in order.iterrows():
            best_boss = None
            best_dmg = 0
            for b in bosses:
                if remaining[b]>0 and p[b]>best_dmg:
                    best_dmg = p[b]
                    best_boss = b
            if best_boss:
                assigns.append({"ผู้เล่น":p["ชื่อ"], "บอส":best_boss, "damage":best_dmg})
                remaining[best_boss] = max(0, remaining[best_boss]-best_dmg)
        snapshot = remaining.copy()
        result.append({"day":day,"assigns":assigns,"snapshot":snapshot})
    st.session_state.plan = result
    st.success(f"สร้างแผนสำเร็จ {day} วัน")

# --- แสดงผลแผน ---
if "plan" in st.session_state and st.session_state.plan:
    st.subheader("แผนการต่อสู้")
    for r in st.session_state.plan:
        st.markdown(f"**วัน {r['day']}** — HP คงเหลือ: " +
                    f"เทโอ {r['snapshot']['เทโอ']:,} | ไคล์ {r['snapshot']['ไคล์']:,} | " +
                    f"ยอนฮี {r['snapshot']['ยอนฮี']:,} | คาร์ม่า {r['snapshot']['คาร์ม่า']:,}")
        for a in r["assigns"]:
            st.markdown(f"- {a['ผู้เล่น']} → {a['บอส']} ({fmtM(a['damage'])})")
        st.markdown("---")

# --- Export CSV/XLSX ---
st.subheader("ส่งออกข้อมูล")
if st.session_state.get("plan"):
    plan_df = pd.DataFrame([
        {"วัน":d["day"], "ผู้เล่น":a["ผู้เล่น"], "บอส":a["บอส"], "damage":a["damage"]}
        for d in st.session_state.plan for a in d["assigns"]
    ])
    csv = plan_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("ส่งออก CSV", csv, file_name=f"{guild_name or 'guild'}_plan.csv", mime="text/csv")
    xlsx = plan_df.to_excel(index=False, engine="openpyxl")
    st.download_button("ส่งออก XLSX", plan_df.to_excel(index=False, engine="openpyxl"), file_name=f"{guild_name or 'guild'}_plan.xlsx")
