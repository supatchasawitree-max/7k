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
// --- ตัวแปรและ Helpers ---
let players = [];

function parseDamage(val){
  if(!val) return 0;
  let s = String(val).trim().toLowerCase().replace(/,/g,'');
  if(s.endsWith('m')) return Math.round(parseFloat(s)*1000000);
  if(s.endsWith('k')) return Math.round(parseFloat(s)*1000);
  return Math.round(parseFloat(s)||0);
}
function fmtM(n){ return (n/1e6).toFixed(3).replace(/\.0+$/,'') + 'M'; }

// --- Table ---
function refreshTable(){
  const body=document.getElementById('playersBody');
  body.innerHTML='';
  if(players.length===0){
    for(let i=0;i<5;i++) players.push({name:`Player${i+1}`,teo:'',kyle:'',yoonhee:'',karma:''});
  }
  const max=Number(document.getElementById('maxPlayers').value)||30;
  players = players.slice(0,max);

  players.forEach((p)=>{
    const tr=document.createElement('tr');
    tr.innerHTML=`
      <td></td>
      <td><input class="form-control form-control-sm name" value="${p.name}"></td>
      <td><input class="form-control form-control-sm teo" value="${p.teo}"></td>
      <td><input class="form-control form-control-sm kyle" value="${p.kyle}"></td>
      <td><input class="form-control form-control-sm yoonhee" value="${p.yoonhee}"></td>
      <td><input class="form-control form-control-sm karma" value="${p.karma}"></td>
      <td><button class="btn btn-sm btn-danger removeBtn">ลบ</button></td>
    `;
    body.appendChild(tr);
    tr.querySelector('td:first-child').textContent = body.children.length;

    tr.querySelector('.removeBtn').onclick = (e)=>{
      const row = e.target.closest('tr');
      const index = Array.from(body.children).indexOf(row);
      if(index > -1){
        players.splice(index, 1);
        refreshTable();
      }
    };
  });
}

function readTable(){
  const rows = [...document.querySelectorAll('#playersBody tr')];
  players = rows.map((tr,i)=>({
    name: tr.querySelector('.name').value || `Player${i+1}`,
    teo: tr.querySelector('.teo').value,
    kyle: tr.querySelector('.kyle').value,
    yoonhee: tr.querySelector('.yoonhee').value,
    karma: tr.querySelector('.karma').value
  }));
  return players;
}

// --- Add / Clear ---
document.getElementById('addRow').onclick = ()=>{
  readTable();
  players.push({name:`Player${players.length+1}`,teo:'',kyle:'',yoonhee:'',karma:''});
  refreshTable();
};
document.getElementById('clearBtn').onclick = ()=>{
  if(confirm('ล้างทั้งหมด?')) { players=[]; refreshTable(); }
};

// --- Import CSV/XLSX ---
const fileInput = document.getElementById('fileInput');
document.getElementById('importFile').onclick = ()=> fileInput.click();
fileInput.onchange = e=>{
  const f=e.target.files[0]; if(!f) return;
  const reader = new FileReader();
  reader.onload = ev=>{
    if(f.name.endsWith('.csv')||f.name.endsWith('.tsv')) parseTextToTable(ev.target.result);
    else{
      const wb = XLSX.read(new Uint8Array(ev.target.result), {type:'array'});
      const ws = wb.Sheets[wb.SheetNames[0]];
      const json = XLSX.utils.sheet_to_json(ws,{header:1});
      parseTextToTable(json.map(r=>r.join('\\t')).join('\\n'));
    }
  };
  if(f.name.endsWith('.csv')||f.name.endsWith('.tsv')) reader.readAsText(f);
  else reader.readAsArrayBuffer(f);
};

function parseTextToTable(text){
  const rows=text.split(/\\r?\\n/).map(l=>l.trim()).filter(l=>l);
  const parsed=rows.map(l=>l.split(/\\t|,/));
  let newPlayers=[];
  let start=0;
  if(parsed[0] && parsed[0][0].toLowerCase().includes('name')) start=1;
  for(let i=start;i<parsed.length;i++){
    const r=parsed[i]; if(r.length<5) continue;
    newPlayers.push({name:r[0],teo:r[1],kyle:r[2],yoonhee:r[3],karma:r[4]});
  }
  if(newPlayers.length){ players = newPlayers; refreshTable(); alert('นำเข้า '+newPlayers.length+' แถว'); }
}

// --- Paste from Clipboard ---
document.getElementById('pasteBtn').onclick = ()=>navigator.clipboard.readText().then(parseTextToTable);

// --- Google Sheet Import ---
document.getElementById('importSheetBtn').onclick = async ()=>{
  const url = prompt("วางลิงก์ Google Sheet (Anyone with link - Viewer)");
  if(!url) return;
  try{
    const idMatch = url.match(/spreadsheets\\/d\\/([a-zA-Z0-9_-]+)/);
    if(!idMatch){ alert('ไม่พบ Sheet ID'); return; }
    const id=idMatch[1];
    const gidMatch = url.match(/gid=(\\d+)/);
    const gid = gidMatch ? gidMatch[1] : '0';
    const csvUrl=`https://docs.google.com/spreadsheets/d/${id}/export?format=csv&gid=${gid}`;
    const resp = await fetch(csvUrl);
    const text = await resp.text();
    if(text.startsWith('<')){ alert('Sheet ไม่ได้ตั้งสาธารณะ'); return; }
    parseTextToTable(text);
    alert('นำเข้าจาก Google Sheet สำเร็จ!');
  }catch(e){ alert('นำเข้าไม่สำเร็จ'); }
};

// --- Generate Plan ---
document.getElementById('generateBtn').onclick = ()=>{
  const pl = readTable().map(p=>({
    name:p.name,
    teo:parseDamage(p.teo), kyle:parseDamage(p.kyle), yoonhee:parseDamage(p.yoonhee), karma:parseDamage(p.karma)
  }));
  const hp = {
    teo:Number(document.getElementById('hp_teo').value)||0,
    kyle:Number(document.getElementById('hp_kyle').value)||0,
    yoonhee:Number(document.getElementById('hp_yoonhee').value)||0,
    karma:Number(document.getElementById('hp_karma').value)||0
  };
  const bosses=['teo','kyle','yoonhee','karma'];
  const remaining={...hp};
  const result=[];
  let day=0;
  while(Object.values(remaining).some(v=>v>0) && day<500){
    day++;
    const order=pl.slice().sort((a,b)=>Math.max(b.teo,b.kyle,b.yoonhee,b.karma)-Math.max(a.teo,a.kyle,a.yoonhee,a.karma));
    const assigns=[];
    for(const p of order){
      let best=null, bestD=0;
      for(const b of bosses){ if(remaining[b]>0 && p[b]>bestD){best=p[b]; bestD=b;} }
      let target=null;
      for(const b of bosses){
        if(remaining[b]>0 && p[b]>0 && p[b]>=bestD){
          bestD=p[b]; target=b;
        }
      }
      if(target){ assigns.push({player:p.name,boss:target,damage:p[target]}); remaining[target]=Math.max(0,remaining[target]-p[target]); }
    }
    result.push({day,assigns,snapshot:{...remaining}});
  }
  window._lastPlan = result;
  renderResult(result);
};

// --- Render Plan ---
function renderResult(res){
  const area=document.getElementById('resultArea'); area.innerHTML='';
  res.forEach(r=>{
    const card=document.createElement('div'); card.className='p-3 mb-2 bg-white rounded';
    let html=`<strong>Day ${r.day}</strong><div class='small-muted'>HP Left — Teo: ${r.snapshot.teo.toLocaleString()} / Kyle: ${r.snapshot.kyle.toLocaleString()} / Yoonhee: ${r.snapshot.yoonhee.toLocaleString()} / Karma: ${r.snapshot.karma.toLocaleString()}</div><div class='row mt-2'>`;
    r.assigns.forEach(a=> html+=`<div class='col-md-6 mb-2'><div class='p-2 border rounded'><strong>${a.player}</strong><div class='small-muted'>${a.boss.toUpperCase()} • ${a.damage.toLocaleString()} (${fmtM(a.damage)})</div></div></div>`);
    html+='</div>'; card.innerHTML=html; area.appendChild(card);
  });
}

// --- Export CSV/XLSX ---
document.getElementById('exportCsv').onclick = ()=>{
  const plan = window._lastPlan||[]; if(!plan.length){alert('ไม่มีแผน'); return;}
  const rows=[["Day","Player","Boss","Damage"]];
  plan.forEach(d=>d.assigns.forEach(a=>rows.push([d.day,a.player,a.boss.toUpperCase(),a.damage])));
  const csv=rows.map(r=>r.join(',')).join('\\n');
  const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download=(document.getElementById('guildName').value||'guild')+"_plan.csv"; a.click();
};
document.getElementById('exportXlsx').onclick = ()=>{
  const plan = window._lastPlan||[]; if(!plan.length){alert('ไม่มีแผน'); return;}
  const aoa=[["Day","Player","Boss","Damage"]];
  plan.forEach(d=>d.assigns.forEach(a=>aoa.push([d.day,a.player,a.boss.toUpperCase(),a.damage])));
  const wb=XLSX.utils.book_new(); const ws=XLSX.utils.aoa_to_sheet(aoa);
  XLSX.utils.book_append_sheet(wb,ws,'Plan'); XLSX.writeFile(wb,(document.getElementById('guildName').value||'guild')+"_plan.xlsx");
};

// --- Copy Markdown ---
document.getElementById('copyMd').onclick = ()=>{
  const plan = window._lastPlan||[]; if(!plan.length){alert('ไม่มีแผน'); return;}
  const lines=[`# ${(document.getElementById('guildName').value||'Guild')} — Raid Plan (${plan.length} days)`];
  plan.forEach(d=>{
    lines.push(`**Day ${d.day}**`);
    d.assigns.forEach(a=> lines.push(`- ${a.player} → ${a.boss.toUpperCase()} (${fmtM(a.damage)})`));
    lines.push('');
  });
  navigator.clipboard.writeText(lines.join('\\n')).then(()=>alert('คัดลอกเรียบร้อย!'));
};

// เริ่มต้น
refreshTable();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=True)
