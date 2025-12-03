import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="7K Guild Boss Planner", layout="wide")

html_code = """
<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>ตัววางแผน Guild Boss Seven Knight</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/xlsx/dist/xlsx.full.min.js"></script>
<style>
  body { background: #f5f7fb; }
  .accent { color: #7c3aed; font-weight:700; }
  .card { border-radius: 12px; }
  .small-muted { color:#6c757d; font-size:0.9rem; }
  .btn-ghost { background:transparent; border:1px solid rgba(0,0,0,0.06); }
</style>
</head>
<body>
<div class="container py-4">
  <div class="card p-4 shadow-sm">
    <div class="d-flex align-items-start mb-3">
      <div>
        <h3 class="mb-0">ตัววางแผน Guild Boss Seven Knight</h3>
        <div class="small-muted">HTML แยก — นำเข้า Google Sheet (สาธารณะ), CSV/XLSX, หรือวางข้อมูล — ไม่ต้องล็อกอิน</div>
      </div>
      <div class="ms-auto text-end small-muted">สร้างโดย <span class="accent">ZeRo</span></div>
    </div>

    <div class="row g-2 mb-3">
      <div class="col-md-4">
        <label class="form-label">ชื่อกิลด์</label>
        <input id="guildName" class="form-control" placeholder="ใส่ได้ (สำหรับชื่อไฟล์ส่งออก)">
      </div>
      <div class="col-md-4">
        <label class="form-label">จำนวนผู้เล่น (สูงสุด 30)</label>
        <input id="maxPlayers" class="form-control" type="number" value="30" min="1" max="30">
      </div>
      <div class="col-md-4">
        <label class="form-label">HP ของบอสเริ่มต้น</label>
        <input id="defaultHP" class="form-control" type="number" value="100000000">
      </div>
    </div>

    <div class="mb-2 d-flex justify-content-between align-items-center">
      <h6 class="mb-0">ผู้เล่น (ชื่อ | Teo | Kyle | Yoonhee | Karma)</h6>
      <div class="small-muted">รับค่ารูปแบบ เช่น <code>1.540m</code>, <code>980k</code>, <code>1540000</code></div>
    </div>

    <div class="table-responsive mb-2">
      <table class="table table-bordered" id="playersTable">
        <thead class="table-light">
          <tr>
            <th style="width:40px">#</th>
            <th>ชื่อ</th>
            <th>Teo</th>
            <th>Kyle</th>
            <th>Yoonhee</th>
            <th>Karma</th>
            <th style="width:90px">จัดการ</th>
          </tr>
        </thead>
        <tbody id="playersBody"></tbody>
      </table>
    </div>

    <div class="mb-3 d-flex gap-2 flex-wrap">
      <button id="addRow" class="btn btn-sm btn-success">+ เพิ่มแถว</button>
      <input type="file" id="fileInput" accept=".csv,.tsv,.xlsx,.xls" style="display:none">
      <button id="importFile" class="btn btn-sm btn-warning">นำเข้า CSV/XLSX</button>
      <button id="pasteBtn" class="btn btn-sm btn-primary">วางจากคลิปบอร์ด</button>
      <button id="importSheetBtn" class="btn btn-sm btn-info">นำเข้า Google Sheet (URL)</button>
      <button id="clearBtn" class="btn btn-sm btn-outline-danger">ล้างทั้งหมด</button>
    </div>

    <div class="row g-2 mb-3">
      <div class="col-md-3">
        <label class="form-label">HP Teo</label>
        <input id="hp_teo" class="form-control" type="number" value="100000000">
      </div>
      <div class="col-md-3">
        <label class="form-label">HP Kyle</label>
        <input id="hp_kyle" class="form-control" type="number" value="100000000">
      </div>
      <div class="col-md-3">
        <label class="form-label">HP Yoonhee</label>
        <input id="hp_yoonhee" class="form-control" type="number" value="100000000">
      </div>
      <div class="col-md-3">
        <label class="form-label">HP Karma</label>
        <input id="hp_karma" class="form-control" type="number" value="100000000">
      </div>
    </div>

    <div class="mb-3 d-flex gap-2">
      <button id="generateBtn" class="btn btn-lg btn-primary">สร้างแผน (ปรับอัตโนมัติ)</button>
      <button id="exportCsv" class="btn btn-dark">ส่งออก CSV</button>
      <button id="exportXlsx" class="btn btn-secondary">ส่งออก XLSX</button>
      <button id="copyMd" class="btn btn-outline-secondary">คัดลอก Markdown สำหรับ Discord</button>
    </div>

    <hr>

    <div id="resultArea"></div>

    <div class="mt-3 small-muted text-end">สร้างโดย <span class="accent">ZeRo</span></div>
  </div>
</div>

<script>
// --- วาง JavaScript ของคุณทั้งหมดที่นี่ ---
// ฟังก์ชัน parseDamage, refreshTable, readTable, import, generate plan, export, copyMD ฯลฯ
refreshTable();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=True)
