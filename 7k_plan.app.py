<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>ตัวช่วยวางแผนกิลด์บอส Seven Knights v3 (นำเข้า Google Sheet)</title>
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
        <h3 class="mb-0">ตัวช่วยวางแผนกิลด์บอส Seven Knights</h3>
        <div class="small-muted">ไฟล์ HTML เดี่ยว — นำเข้า Google Sheet (สาธารณะ), CSV/XLSX หรือวางข้อมูลได้ — ไม่ต้องล็อกอิน</div>
      </div>
      <div class="ms-auto text-end small-muted">สร้างโดย <span class="accent">ZeRo</span></div>
    </div>

    <div class="row g-2 mb-3">
      <div class="col-md-4">
        <label class="form-label">ชื่อกิลด์</label>
        <input id="guildName" class="form-control" placeholder="ไม่จำเป็น (ใช้ตั้งชื่อไฟล์ตอนส่งออก)">
      </div>
      <div class="col-md-4">
        <label class="form-label">จำนวนผู้เล่น (สูงสุด 30)</label>
        <input id="maxPlayers" class="form-control" type="number" value="30" min="1" max="30">
      </div>
      <div class="col-md-4">
        <label class="form-label">HP บอสเริ่มต้น (ค่าเริ่มต้น)</label>
        <input id="defaultHP" class="form-control" type="number" value="100000000">
      </div>
    </div>

    <div class="mb-2 d-flex justify-content-between align-items-center">
      <h6 class="mb-0">ผู้เล่น (ชื่อ | เทโอ | ไคล์ | ยอนฮี | คาร์ม่า)</h6>
      <div class="small-muted">รองรับรูปแบบคะแนนเช่น <code>1.540m</code>, <code>980k</code>, <code>1540000</code></div>
    </div>

    <div class="table-responsive mb-2">
      <table class="table table-bordered" id="playersTable">
        <thead class="table-light">
          <tr>
            <th style="width:40px">#</th>
            <th>ชื่อผู้เล่น</th>
            <th>เทโอ</th>
            <th>ไคล์</th>
            <th>ยอนฮี</th>
            <th>คาร์ม่า</th>
            <th style="width:90px">ลบ</th>
          </tr>
        </thead>
        <tbody id="playersBody"></tbody>
      </table>
    </div>

    <div class="mb-3 d-flex gap-2 flex-wrap">
      <button id="addRow" class="btn btn-sm btn-success">+ เพิ่มแถว</button>
      <input type="file" id="fileInput" accept=".csv,.tsv,.xlsx,.xls" style="display:none">
      <button id="importFile" class="btn btn-sm btn-warning">นำเข้า CSV/XLSX</button>
      <button id="pasteBtn" class="btn btn-sm btn-primary">วางข้อมูลจากคลิปบอร์ด</button>
      <button id="importSheetBtn" class="btn btn-sm btn-info">นำเข้า Google Sheet (ลิงก์)</button>
      <button id="clearBtn" class="btn btn-sm btn-outline-danger">ล้างข้อมูลทั้งหมด</button>
    </div>

    <div class="row g-2 mb-3">
      <div class="col-md-3">
        <label class="form-label">HP เทโอ</label>
        <input id="hp_teo" class="form-control" type="number" value="100000000">
      </div>
      <div class="col-md-3">
        <label class="form-label">HP ไคล์</label>
        <input id="hp_kyle" class="form-control" type="number" value="100000000">
      </div>
      <div class="col-md-3">
        <label class="form-label">HP ยอนฮี</label>
        <input id="hp_yoonhee" class="form-control" type="number" value="100000000">
      </div>
      <div class="col-md-3">
        <label class="form-label">HP คาร์ม่า</label>
        <input id="hp_karma" class="form-control" type="number" value="100000000">
      </div>
    </div>

    <div class="mb-3 d-flex gap-2">
      <button id="generateBtn" class="btn btn-lg btn-primary">สร้างแผนการตี (Auto Optimize)</button>
      <button id="exportCsv" class="btn btn-dark">ส่งออก CSV</button>
      <button id="exportXlsx" class="btn btn-secondary">ส่งออก XLSX</button>
      <button id="copyMd" class="btn btn-outline-secondary">คัดลอกเป็น Markdown (Discord)</button>
    </div>

    <hr>

    <div id="resultArea"></div>

    <div class="mt-3 small-muted text-end">สร้างโดย <span class="accent">ZeRo</span></div>
  </div>
</div>

<script>
// ไม่มีการแก้โค้ด JavaScript — มีการเปลี่ยนเฉพาะข้อความ alert, ปุ่ม, label ให้เป็นภาษาไทย

// Helpers
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

// Table
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
  return tr;
}

function refreshTable(){
  const body=document.getElementById('playersBody');
  body.innerHTML='';
  let players=loadPlayers()||[];
  if(players.length===0){ for(let i=0;i<5;i++) players.push({name:`ผู้เล่น${i+1}`,teo:'',kyle:'',yoonhee:'',karma:''}); }
  const max=Number(maxPlayers.value)||30;
  players=players.slice(0,max);
  players.forEach((p,i)=>{
    const tr=createRow(i,p); body.appendChild(tr);
    tr.querySelector('.removeBtn').onclick=()=>{ players.splice(i,1); savePlayers(players); refreshTable(); };
  });
  savePlayers(players);
}

function readTable(){
  const rows=[...document.querySelectorAll('#playersBody tr')];
  const p=rows.map((tr,i)=>({
    name: tr.querySelector('.name').value||`ผู้เล่น${i+1}`,
    teo: tr.querySelector('.teo').value,
    kyle: tr.querySelector('.kyle').value,
    yoonhee: tr.querySelector('.yoonhee').value,
    karma: tr.querySelector('.karma').value,
  }));
  savePlayers(p); return p;
}

// File import
importFile.onclick=()=>fileInput.click();
fileInput.onchange=e=>{
  const f=e.target.files[0]; if(!f) return;
  const reader=new FileReader();
  reader.onload=ev=>{
    if(f.name.endsWith('.csv')||f.name.endsWith('.tsv')) parseTextToTable(ev.target.result);
    else{
      const wb=XLSX.read(new Uint8Array(ev.target.result),{type:'array'});
      const ws=wb.Sheets[wb.SheetNames[0]];
      const json=XLSX.utils.sheet_to_json(ws,{header:1});
      parseTextToTable(json.map(r=>r.join('\t')).join('\n'));
    }
  };
  if(f.name.endsWith('.csv')||f.name.endsWith('.tsv')) reader.readAsText(f);
  else reader.readAsArrayBuffer(f);
};

function parseTextToTable(text){
  const rows=text.split(/\r?\n/).map(l=>l.trim()).filter(l=>l);
  const parsed=rows.map(l=>l.split(/\t|,/));
  const players=[];
  let start=0;
  if(parsed[0] && parsed[0][0].toLowerCase().includes('name')) start=1;
  for(let i=start;i<parsed.length;i++){
    const r=parsed[i]; if(r.length<5) continue;
    players.push({name:r[0],teo:r[1],kyle:r[2],yoonhee:r[3],karma:r[4]});
  }
  if(players.length){ savePlayers(players); refreshTable(); alert('นำเข้าแล้ว '+players.length+' แถว'); }
}

// Paste
pasteBtn.onclick=()=>navigator.clipboard.readText().then(parseTextToTable);

// NEW Google Sheet Import
importSheetBtn.onclick = async ()=>{
  const url = prompt("วางลิงก์ Google Sheet ที่ตั้งค่าให้ ‘ทุกคนที่มีลิงก์สามารถดูได้’");
  if(!url) return;

  try{
    const idMatch = url.match(/spreadsheets\/d\/([a-zA-Z0-9_-]+)/);
    if(!idMatch){ alert('ไม่พบรหัสเอกสาร Sheet'); return; }
    const id=idMatch[1];

    const gidMatch = url.match(/gid=(\d+)/);
    const gid = gidMatch ? gidMatch[1] : '0';

    const csvUrl=`https://docs.google.com/spreadsheets/d/${id}/export?format=csv&gid=${gid}`;
    const resp = await fetch(csvUrl);
    const text = await resp.text();

    if(text.startsWith('<')){
      alert('Sheet นี้ไม่ได้ตั้งเป็นสาธารณะ (Google ส่งหน้า HTML กลับมา)');
      return;
    }
    parseTextToTable(text);
    alert('นำเข้าข้อมูลจาก Google Sheet สำเร็จ!');
  }catch(e){ alert('นำเข้าข้อมูลล้มเหลว!'); }
};

// Add row
addRow.onclick=()=>{ const p=readTable(); p.push({name:`ผู้เล่น${p.length+1}`,teo:'',kyle:'',yoonhee:'',karma:''}); savePlayers(p); refreshTable(); };

// Clear
clearBtn.onclick=()=>{ if(confirm('ต้องการล้างข้อมูลทั้งหมดหรือไม่?')){ localStorage.removeItem('sk_players'); refreshTable(); } };

// Generate plan
generateBtn.onclick=()=>{
  const players=readTable().map(p=>({
    name:p.name,
    teo:parseDamage(p.teo), kyle:parseDamage(p.kyle), yoonhee:parseDamage(p.yoonhee), karma:parseDamage(p.karma)
  }));

  const hp={
    teo:Number(hp_teo.value)||0,
    kyle:Number(hp_kyle.value)||0,
    yoonhee:Number(hp_yoonhee.value)||0,
    karma:Number(hp_karma.value)||0
  };

  const bosses=['teo','kyle','yoonhee','karma'];
  const remaining={...hp};
  const result=[];
  let day=0;

  while(Object.values(remaining).some(v=>v>0) && day<500){
    day++;
    const order=players.slice().sort((a,b)=>Math.max(b.teo,b.kyle,b.yoonhee,b.karma)-Math.max(a.teo,a.kyle,a.yoonhee,a.karma));
    const assigns=[];

    for(const p of order){
      let best=null, bestD=0;
      for(const b of bosses){ if(remaining[b]>0 && p[b]>bestD){bestD=p[b]; best=b;} }
      if(best){ assigns.push({player:p.name,boss:best,damage:bestD}); remaining[best]=Math.max(0,remaining[best]-bestD); }
    }

    result.push({day,assigns,snapshot:{...remaining}});
  }

  window._lastPlan=result;
  renderResult(result);
};

// Render
function renderResult(res){
  const area=resultArea; area.innerHTML='';
  res.forEach(r=>{
    const card=document.createElement('div'); card.className='p-3 mb-2 bg-white rounded';
    let html=`<strong>วันที่ ${r.day}</strong><div class='small-muted'>HP คงเหลือ — เทโอ: ${r.snapshot.teo.toLocaleString()} / ไคล์: ${r.snapshot.kyle.toLocaleString()} / ยอนฮี: ${r.snapshot.yoonhee.toLocaleString()} / คาร์ม่า: ${r.snapshot.karma.toLocaleString()}</div><div class='row mt-2'>`;
    r.assigns.forEach(a=> html+=`<div class='col-md-6 mb-2'><div class='p-2 border rounded'><strong>${a.player}</strong><div class='small-muted'>${a.boss.toUpperCase()} • ${a.damage.toLocaleString()} (${fmtM(a.damage)})</div></div></div>`);
    html+='</div>'; card.innerHTML=html; area.appendChild(card);
  });
}

// Export CSV
exportCsv.onclick=()=>{
  const plan=window._lastPlan||[]; if(!plan.length){alert('ยังไม่มีแผน');return;}
  const rows=[["Day","Player","Boss","Damage"]];
  plan.forEach(d=>d.assigns.forEach(a=>rows.push([d.day,a.player,a.boss.toUpperCase(),a.damage])));
  const csv=rows.map(r=>r.join(',')).join('\n');
  const blob=new Blob([csv],{type:'text/csv;charset=utf-8;'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download=(guildName.value||'guild')+"_plan.csv"; a.click();
};

// Export XLSX
exportXlsx.onclick=()=>{
  const plan=window._lastPlan||[]; if(!plan.length){alert('ยังไม่มีแผน');return;}
  const aoa=[["Day","Player","Boss","Damage"]];
  plan.forEach(d=>d.assigns.forEach(a=>aoa.push([d.day,a.player,a.boss.toUpperCase(),a.damage])));
  const wb=XLSX.utils.book_new(); const ws=XLSX.utils.aoa_to_sheet(aoa);
  XLSX.utils.book_append_sheet(wb,ws,'Plan');
  XLSX.writeFile(wb,(guildName.value||'guild')+"_plan.xlsx");
};

// Copy MD
copyMd.onclick=()=>{
  const plan=window._lastPlan||[]; if(!plan.length){alert('ยังไม่มีแผน');return;}
  const lines=[`# ${(guildName.value||'Guild')} — แผนการตี (${plan.length} วัน)`];
  plan.forEach(d=>{
    lines.push(`**วันที่ ${d.day}**`);
    d.assigns.forEach(a=> lines.push(`- ${a.player} → ${a.boss.toUpperCase()} (${fmtM(a.damage)})`));
    lines.push('');
  });
  navigator.clipboard.writeText(lines.join('\n')).then(()=>alert('คัดลอกแล้ว!'));
};

refreshTable();
</script>
</body>
</html>
