<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>ตัววางแผน Guild Boss Seven Knight v3</title>
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
            <th style="width:90px">ลบ</th>
          </tr>
        </thead>
        <tbody id="playersBody"></tbody>
      </table>
    </div>

    <div class="mb-3 d-flex gap-2 flex-wrap">
      <button id="addRow" class="btn btn-sm btn-success">+ เพิ่มผู้เล่น</button>
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
// --- Helpers ---
function parseDamage(val){
  if(!val) return 0;
  let s = String(val).trim().toLowerCase().replace(/,/g,'');
  if(s.endsWith('m')) return Math.round(parseFloat(s)*1000000);
  if(s.endsWith('k')) return Math.round(parseFloat(s)*1000);
  return Math.round(parseFloat(s)||0);
}
function fmtM(n){ return (n/1e6).toFixed(3).replace(/\.0+$/,'') + 'M'; }
function savePlayers(p){ localStorage.setItem('sk_players', JSON.stringify(p)); }
function loadPlayers(){ try{ return JSON.parse(localStorage.getItem('sk_players'))||null; }catch{return null;} }

// --- Table ---
function createRow(i,p){
  const tr=document.createElement('tr');
  tr.innerHTML = `
    <td>${i+1}</td>
    <td><input class="form-control form-control-sm name" value="${p?.name||''}"></td>
    <td><input class="form-control form-control-sm teo" value="${p?.teo||''}"></td>
    <td><input class="form-control form-control-sm kyle" value="${p?.kyle||''}"></td>
    <td><input class="form-control form-control-sm yoonhee" value="${p?.yoonhee||''}"></td>
    <td><input class="form-control form-control-sm karma" value="${p?.karma||''}"></td>
    <td><button class="btn btn-sm btn-danger removeBtn">ลบ</button></td>`;
  tr.querySelector('.removeBtn').onclick=()=>{ 
    const players=readTable();
    players.splice(i,1);
    savePlayers(players);
    refreshTable();
  };
  return tr;
}

function refreshTable(){
  const body=document.getElementById('playersBody');
  body.innerHTML='';
  let players=loadPlayers()||[];
  if(players.length===0){ for(let i=0;i<5;i++) players.push({name:`Player${i+1}`,teo:'',kyle:'',yoonhee:'',karma:''}); }
  const max=Number(document.getElementById('maxPlayers').value)||30;
  players=players.slice(0,max);
  players.forEach((p,i)=> body.appendChild(createRow(i,p)));
  savePlayers(players);
}

function readTable(){
  const rows=[...document.querySelectorAll('#playersBody tr')];
  const p=rows.map((tr,i)=>({
    name: tr.querySelector('.name').value||`Player${i+1}`,
    teo: tr.querySelector('.teo').value,
    kyle: tr.querySelector('.kyle').value,
    yoonhee: tr.querySelector('.yoonhee').value,
    karma: tr.querySelector('.karma').value,
  }));
  savePlayers(p); return p;
}

// --- Add Row ---
document.getElementById('addRow').onclick = ()=>{
  const p=readTable();
  p.push({name:`Player${p.length+1}`,teo:'',kyle:'',yoonhee:'',karma:''});
  savePlayers(p);
  refreshTable();
};

// --- Clear ---
document.getElementById('clearBtn').onclick = ()=>{
  if(confirm('ล้างข้อมูลทั้งหมด?')){
    localStorage.removeItem('sk_players');
    refreshTable();
  }
};

// --- Generate Plan ---
document.getElementById('generateBtn').onclick = ()=>{
  const pl = readTable().map(p=>({
    name:p.name,
    teo:parseDamage(p.teo), 
    kyle:parseDamage(p.kyle), 
    yoonhee:parseDamage(p.yoonhee), 
    karma:parseDamage(p.karma)
  }));
  
  const hp = {
    teo:Number(document.getElementById('hp_teo').value)||0,
    kyle:Number(document.getElementById('hp_kyle').value)||0,
    yoonhee:Number(document.getElementById('hp_yoonhee').value)||0,
    karma:Number(document.getElementById('hp_karma').value)||0
  };

  const bosses=['teo','kyle','yoonhee','karma'];
  const result=[];
  let remaining={...hp};
  let day=0;

  while(Object.values(remaining).some(v=>v>0) && day<500){
    day++;
    const assigns=[];
    pl.forEach(p=>{
      let target = bosses.filter(b=>remaining[b]>0).sort((a,b)=>p[b]-p[a])[0];
      if(target){
        const dmg = Math.min(p[target], remaining[target]);
        assigns.push({player:p.name,boss:target,damage:dmg});
        remaining[target]-=dmg;
      }
    });
    result.push({day,assigns,snapshot:{...remaining}});
  }
  window._lastPlan = result;
  renderResult(result);
};

// --- Render Result ---
function renderResult(res){
  const area=document.getElementById('resultArea'); area.innerHTML='';
  res.forEach(r=>{
    const card=document.createElement('div'); card.className='p-3 mb-2 bg-white rounded';
    let html=`<strong>Day ${r.day}</strong>
    <div class='small-muted'>HP Left — Teo: ${r.snapshot.teo.toLocaleString()} / Kyle: ${r.snapshot.kyle.toLocaleString()} / Yoonhee: ${r.snapshot.yoonhee.toLocaleString()} / Karma: ${r.snapshot.karma.toLocaleString()}</div>
    <div class='row mt-2'>`;
    r.assigns.forEach(a=> html+=`<div class='col-md-6 mb-2'><div class='p-2 border rounded'><strong>${a.player}</strong><div class='small-muted'>${a.boss.toUpperCase()} • ${a.damage.toLocaleString()} (${fmtM(a.damage)})</div></div></div>`);
    html+='</div>'; card.innerHTML=html; area.appendChild(card);
  });
}

// --- Initialize ---
refreshTable();
</script>
</body>
</html>
