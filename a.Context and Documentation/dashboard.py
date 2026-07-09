# ==========================================================================
# dashboard.py  --  Builds the Morning Dew dashboard HTML file.
# ==========================================================================

import json
from datetime import datetime

import config


def _records(tees_by_course):
    """Flatten {course: [tees]} into one list of the fields the page needs."""
    out = []
    for tees in tees_by_course.values():
        for t in tees:
            out.append({
                "course": t["course"],
                "date":   t["date"],
                "time":   t["time"],
                "day":    t["day_of_week"],
                "holes":  t["holes"],
                "spots":  t["spots"],
                "price":  t["price"],
                "url":    t["booking_url"],
            })
    return out


def build_dashboard(tees_by_course):
    """Write the Morning Dew dashboard HTML file."""
    records = _records(tees_by_course)

    data_json     = json.dumps(records).replace("</", "<\\/")
    defaults_json = json.dumps({
        "days":    config.MATCH_DAYS,
        "start":   config.MATCH_TIME_START,
        "end":     config.MATCH_TIME_END,
        "players": config.PLAYERS,
        "holes":   config.HOLES,
    })
    enabled_courses = sorted(
        c["name"] for c in config.COURSES if c.get("enabled", True)
    )
    courses_json = json.dumps(enabled_courses)

    html = (_TEMPLATE
            .replace("__APPNAME__",   config.APP_NAME)
            .replace("__GENERATED__", _now())
            .replace("__LOOKAHEAD__", str(config.LOOKAHEAD_DAYS))
            .replace("__DATA__",      data_json)
            .replace("__DEFAULTS__",  defaults_json)
            .replace("__COURSES__",   courses_json))

    with open(config.DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(html)


def _now():
    dt = datetime.now(config.TIMEZONE)
    try:
        return dt.strftime("%A, %b %-d %Y at %-I:%M %p %Z")
    except ValueError:
        return dt.strftime("%A, %b %d %Y at %I:%M %p %Z")


# --------------------------------------------------------------------------
# Template — __TOKENS__ replaced by build_dashboard(). Raw string so the
# CSS/JS curly braces need no escaping.
# --------------------------------------------------------------------------
_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__APPNAME__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Hanken+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --navy:#15294a; --carolina:#2f7cb5; --sky:#cfe3f1; --sky-b:#aecde6;
    --paper:#efe9db; --cream:#fbf8f0; --offwhite:#fffdf8;
    --border:#e3dccb; --muted:#8693a5; --body-text:#3a4654;
    --day-bg:#e9f1f8; --day-text:#1c4e74; --day-b:#d3e3f0;
    --row-b:#f1ebdc; --sage-bg:#e6ede2; --sage-text:#4d6b48;
    --th-bg:#f3ece0;
  }
  * { box-sizing:border-box; }
  body {
    margin:0; background:var(--paper);
    font-family:'Hanken Grotesk',sans-serif;
    -webkit-font-smoothing:antialiased; color:var(--navy);
  }
  select { font-family:'Hanken Grotesk',sans-serif; }

  /* ---- Header ---- */
  header { background:var(--cream); border-bottom:1px solid var(--border); }
  .hbar {
    max-width:1240px; margin:0 auto; padding:14px 24px;
    display:flex; align-items:center; justify-content:space-between;
  }
  .brand { display:flex; align-items:center; gap:11px; }
  .wordmark {
    font-family:'Bricolage Grotesque',sans-serif; font-size:26px;
    font-weight:600; color:var(--navy); letter-spacing:-.5px;
  }
  .syf { width:44px; height:44px; display:block; filter:drop-shadow(0 1px 3px #0003); }
  .refreshed { font-size:12px; font-weight:600; color:#56708a; }
  .btn-refresh {
    cursor:pointer; margin-left:12px; border:1.5px solid var(--sky-b);
    background:var(--sky); color:var(--day-text); border-radius:999px;
    padding:6px 14px; font:700 12px/1 'Hanken Grotesk'; white-space:nowrap;
  }
  .btn-refresh:disabled { opacity:.55; cursor:default; }
  .seam { height:3px; background:linear-gradient(90deg,#c39a3e,#7a9a72,#2f7cb5,#15294a); opacity:.5; }

  /* ---- Page layout ---- */
  .layout {
    max-width:1240px; margin:0 auto; padding:24px 24px 60px;
    display:flex; gap:28px; align-items:flex-start;
  }

  /* ---- Filter rail (desktop) ---- */
  .rail {
    width:296px; flex:none; position:sticky; top:20px;
    background:var(--cream); border:1px solid var(--border);
    border-radius:18px; padding:20px;
    box-shadow:0 8px 24px rgba(20,30,55,.06);
  }
  .rail-head {
    display:flex; align-items:center; justify-content:space-between; margin-bottom:18px;
  }
  .rail-title { font-family:'Bricolage Grotesque',sans-serif; font-size:17px; font-weight:600; }
  .btn-reset { cursor:pointer; background:none; border:none; font:700 12px/1 'Hanken Grotesk'; color:var(--carolina); padding:0; }

  /* ---- Filter card (mobile only) ---- */
  .filter-card {
    display:none; background:var(--paper); border-bottom:1px solid #e0d8c6;
    padding:13px 18px 15px; flex-direction:column; gap:11px;
  }

  /* ---- Shared filter controls ---- */
  .flabel {
    display:block; font:700 11px/1 'Hanken Grotesk'; letter-spacing:1.2px;
    text-transform:uppercase; color:var(--muted); margin-bottom:8px;
  }
  .fblock { margin-bottom:16px; }
  .fblock:last-child { margin-bottom:0; }

  /* Day chips */
  .chips { display:flex; gap:5px; flex-wrap:wrap; }
  .day-chip {
    cursor:pointer; user-select:none; border-radius:999px; padding:7px 13px;
    font:700 12.5px/1 'Hanken Grotesk'; background:#fff;
    border:1.5px solid var(--border); color:var(--muted); transition:.12s;
  }
  .day-chip.on { background:var(--sky); border-color:var(--sky-b); color:var(--day-text); }

  /* Time dropdowns */
  .timewrap { display:flex; align-items:center; gap:8px; }
  .timewrap select {
    flex:1; border:1.5px solid var(--border); border-radius:10px; padding:8px 10px;
    font-size:13px; font-weight:600; background:#fff; color:var(--navy); cursor:pointer;
  }
  .timesep { color:var(--muted); font-weight:700; }

  /* Segmented controls (players + holes) */
  .seg { display:flex; background:#fff; border:1.5px solid var(--border); border-radius:11px; padding:3px; }
  .seg-btn {
    flex:1; cursor:pointer; border:none; border-radius:8px; padding:7px 0;
    font:700 13px/1 'Hanken Grotesk'; background:transparent; color:var(--muted); transition:.12s;
  }
  .seg-btn.on { background:var(--navy); color:#fff; }

  /* Inline course list (desktop) */
  .course-list { display:flex; flex-direction:column; gap:1px; }
  .course-item {
    display:flex; align-items:center; gap:10px; padding:7px 4px;
    border-radius:9px; cursor:pointer; font-size:13px; font-weight:600; color:#33414f;
  }
  .course-item:hover { background:#f0e9d8; }
  .cbox {
    width:18px; height:18px; flex:none; border-radius:5px;
    border:1.5px solid #cdd6e0; display:flex; align-items:center;
    justify-content:center; font-size:11px; color:#fff;
  }
  .cbox.on { background:var(--navy); border-color:var(--navy); }
  .btn-small { cursor:pointer; background:none; border:none; font:700 11px/1 'Hanken Grotesk'; color:var(--carolina); padding:0; }

  /* Course popover (mobile) */
  .dd { position:relative; }
  .dd-btn {
    display:flex; align-items:center; gap:6px; cursor:pointer;
    border:1.5px solid var(--border); border-radius:10px; padding:8px 12px;
    font:700 13px/1 'Hanken Grotesk'; background:#fff; color:var(--navy);
  }
  .dd-panel {
    display:none; position:absolute; top:42px; left:0; z-index:60;
    background:#fff; border:1px solid var(--border); border-radius:14px;
    padding:8px; min-width:240px; box-shadow:0 16px 40px rgba(20,30,55,.22);
  }
  .dd-panel.open { display:block; }
  .dd-footer { display:flex; gap:8px; margin-top:6px; border-top:1px solid #eee4d3; padding-top:8px; }
  .dd-footer button {
    flex:1; cursor:pointer; border:1px solid var(--border); border-radius:8px;
    background:#f3eddf; font:700 12px/1 'Hanken Grotesk'; color:var(--navy); padding:7px;
  }
  .dd-footer .btn-done { background:var(--carolina); color:#fff; border-color:var(--carolina); }

  /* ---- Results area ---- */
  .results { flex:1; min-width:0; }
  .results-head { display:flex; align-items:flex-end; margin-bottom:14px; }
  .count-big { font-family:'Bricolage Grotesque',sans-serif; font-size:22px; font-weight:600; }
  .count-big b { color:var(--carolina); }
  .count-sub { font-size:13px; color:var(--muted); margin-top:3px; }
  .count-mobile { display:none; padding:10px 18px; font-size:13.5px; color:#6a7686; }
  .count-mobile b { color:var(--navy); font-size:15px; }

  /* ---- Table card ---- */
  .card {
    background:var(--offwhite); border:1px solid var(--border);
    border-radius:16px; overflow:hidden; box-shadow:0 8px 24px rgba(20,30,55,.06);
  }
  table { width:100%; border-collapse:collapse; }
  thead tr { background:var(--th-bg); }
  th {
    padding:11px 14px; text-align:left;
    font:700 10.5px/1 'Hanken Grotesk'; letter-spacing:1px;
    text-transform:uppercase; color:#9aa5b4; white-space:nowrap;
  }
  th:first-child { padding-left:24px; }
  th:last-child  { padding-right:24px; }
  th.r { text-align:right; }
  th.c { text-align:center; }

  /* Day separator rows */
  tr.day-head td {
    background:var(--day-bg); border-top:1px solid var(--day-b);
    border-bottom:1px solid var(--day-b); padding:10px 24px; cursor:pointer;
  }
  .day-inner { display:flex; align-items:center; justify-content:space-between; }
  .day-label { font:700 11.5px/1 'Hanken Grotesk'; letter-spacing:1.4px; text-transform:uppercase; color:var(--day-text); }
  .day-meta  { display:flex; align-items:center; gap:10px; font:700 11px/1 'Hanken Grotesk'; color:#6f8eaa; }

  /* Data rows */
  td { padding:11px 14px; border-bottom:1px solid var(--row-b); font-size:14px; color:var(--body-text); }
  td:first-child { padding-left:24px; }
  td:last-child  { padding-right:24px; }
  td.tc { text-align:center; }
  td.tr { text-align:right; }
  td.time-cell  { font-weight:700; color:var(--navy); white-space:nowrap; font-size:14.5px; }
  td.price-cell { font-weight:700; color:var(--navy); }
  .spots-pill {
    display:inline-block; min-width:24px; background:var(--sage-bg); color:var(--sage-text);
    font-weight:700; font-size:12.5px; padding:3px 9px; border-radius:999px; text-align:center;
  }
  .btn-book {
    display:inline-block; background:var(--carolina); color:#fff;
    font:700 13px/1 'Hanken Grotesk'; padding:7px 15px; border-radius:9px;
    text-decoration:none; white-space:nowrap;
  }
  .btn-book:hover { background:#266aa0; }

  /* Group (course-aggregated) rows */
  tr.group-head td { background:#f7f2e7; cursor:default; }
  td.group-time { font-weight:700; color:var(--navy); white-space:nowrap; font-size:14px; }
  .group-actions { display:flex; align-items:center; justify-content:flex-end; gap:10px; }
  .expand-lbl {
    font:700 12px/1 'Hanken Grotesk'; color:var(--carolina);
    white-space:nowrap; cursor:pointer; user-select:none;
  }
  .expand-lbl:hover { color:#266aa0; }

  /* Expanded child rows */
  tr.group-child td { background:var(--offwhite); }
  td.child-time { padding-left:34px; color:#6a7686; font-style:italic; font-size:13.5px; }

  /* Empty state */
  .empty { text-align:center; padding:64px 30px; }
  .empty-icon  { font-size:28px; margin-bottom:10px; }
  .empty-title { font-family:'Bricolage Grotesque',sans-serif; font-size:19px; font-weight:600; color:var(--navy); }
  .empty-sub   { font-size:13.5px; color:#7c8aa0; margin-top:6px; }

  /* ---- Responsive ---- */
  @media (max-width:700px) {
    .rail         { display:none; }
    .filter-card  { display:flex; }
    .layout       { padding:0 0 40px; flex-direction:column; gap:0; }
    .results      { padding:0; }
    .results-head { display:none; }
    .count-mobile { display:block; }
    .card         { border-radius:0; border-left:none; border-right:none; box-shadow:none; }
    th.holes-col, td.holes-col { display:none; }
  }
  @media (min-width:701px) {
    .count-mobile { display:none !important; }
  }
</style>
</head>
<body>

<!-- ===== Header ===== -->
<header>
  <div class="hbar">
    <div class="brand">
      <svg class="syf" viewBox="0 0 100 100" aria-label="Steal Your Face">
        <circle cx="50" cy="50" r="47" fill="#fff" stroke="#111" stroke-width="2.5"/>
        <path d="M50 3 A47 47 0 0 1 50 97 Z" fill="#1c46c2"/>
        <path d="M50 3 A47 47 0 0 0 50 97 Z" fill="#e02434"/>
        <polygon points="57,5 44,46 54,46 40,95 52,52 43,52" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/>
        <circle cx="50" cy="50" r="47" fill="none" stroke="#111" stroke-width="2.5"/>
      </svg>
      <span class="wordmark">__APPNAME__</span>
    </div>
    <span class="refreshed">last refreshed __GENERATED__<button class="btn-refresh" id="refreshBtn">↻ Refresh</button></span>
  </div>
</header>
<div class="seam"></div>

<!-- ===== Mobile filter card ===== -->
<div class="filter-card">
  <div class="fblock" style="margin:0">
    <span class="flabel">Days</span>
    <div class="chips" id="dayChipsMob"></div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="flabel" style="margin:0;width:54px;flex:none;">Time</span>
    <div class="timewrap" style="flex:1">
      <select id="tStartMob"></select>
      <span class="timesep">–</span>
      <select id="tEndMob"></select>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="flabel" style="margin:0;width:54px;flex:none;">Players</span>
    <div class="seg" id="playerSegMob" style="flex:1"></div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="flabel" style="margin:0;width:54px;flex:none;">Holes</span>
    <div class="seg" id="holeSegMob" style="flex:1"></div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="flabel" style="margin:0;width:54px;flex:none;">Courses</span>
    <div class="dd">
      <button class="dd-btn" id="ddBtn" type="button">
        <span id="ddBtnLabel">All courses</span>
        <span style="color:var(--muted);font-size:10px;">▾</span>
      </button>
      <div class="dd-panel" id="ddPanel">
        <div id="ddList"></div>
        <div class="dd-footer">
          <button id="ddAll">All</button>
          <button id="ddNone">None</button>
          <button class="btn-done" id="ddDone">Done</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Mobile count -->
<div class="count-mobile" id="countMobile"></div>

<!-- ===== Body ===== -->
<div class="layout">

  <!-- Desktop filter rail -->
  <aside class="rail">
    <div class="rail-head">
      <span class="rail-title">Find a tee time</span>
      <button class="btn-reset" id="resetBtn">↺ Reset</button>
    </div>
    <div class="fblock">
      <span class="flabel">Days</span>
      <div class="chips" id="dayChipsDsk"></div>
    </div>
    <div class="fblock">
      <span class="flabel">Time window</span>
      <div class="timewrap">
        <select id="tStartDsk"></select>
        <span class="timesep">–</span>
        <select id="tEndDsk"></select>
      </div>
    </div>
    <div class="fblock">
      <span class="flabel">Players</span>
      <div class="seg" id="playerSegDsk"></div>
    </div>
    <div class="fblock">
      <span class="flabel">Holes</span>
      <div class="seg" id="holeSegDsk"></div>
    </div>
    <div class="fblock">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <span class="flabel" style="margin:0">Courses</span>
        <span>
          <button class="btn-small" id="dskAll">All</button>
          &nbsp;·&nbsp;
          <button class="btn-small" id="dskNone">None</button>
        </span>
      </div>
      <div class="course-list" id="courseListDsk"></div>
    </div>
  </aside>

  <!-- Results -->
  <section class="results">
    <div class="results-head">
      <div>
        <div class="count-big" id="countDsk"></div>
        <div class="count-sub">last refreshed __GENERATED__</div>
      </div>
    </div>
    <div class="card">
      <div id="board"></div>
    </div>
  </section>

</div><!-- /.layout -->

<script>
const DATA     = __DATA__;
const DEFAULTS = __DEFAULTS__;

const ABBR = {Sunday:"Sun",Monday:"Mon",Tuesday:"Tue",Wednesday:"Wed",Thursday:"Thu",Friday:"Fri",Saturday:"Sat"};
const COURSES     = __COURSES__;
const PLAYER_OPTS = [{v:1,l:"1+"},{v:2,l:"2+"},{v:3,l:"3+"},{v:4,l:"4"}];
const HOLE_OPTS   = [{v:"any",l:"Any"},{v:9,l:"9"},{v:18,l:"18"}];

// ---- helpers ----
const toMin      = t => { const [h,m]=t.split(':').map(Number); return h*60+m; };
const fmtPrice   = p => (p===null||p===undefined) ? "—" : "$"+Math.round(p);
const fmtTime    = t => { let [h,m]=t.split(':').map(Number); const ap=h<12?"AM":"PM"; let hh=h%12||12; return hh+":"+String(m).padStart(2,'0')+" "+ap; };
const prettyDate = d => new Date(d+"T00:00:00").toLocaleDateString(undefined,{month:'short',day:'numeric'});

// ---- Shared filter state ----
let selDates   = new Set();
let selCourses = new Set(COURSES);
let selPlayers = DEFAULTS.players;
let selHoles   = DEFAULTS.holes;   // number or "any"
let selStart   = DEFAULTS.start;
let selEnd     = DEFAULTS.end;
const dayOpen  = {};               // date -> bool

// Build date list from data
const dateDow = {};
DATA.forEach(d => { dateDow[d.date] = d.day; });
const sortedDates = Object.keys(dateDow).sort();
sortedDates.forEach(date => {
  if(DEFAULTS.days.includes(dateDow[date])) selDates.add(date);
  dayOpen[date] = true;
});

// ==============================
// Day chips
// ==============================
function buildChips(id){
  const box = document.getElementById(id);
  sortedDates.forEach(date => {
    const dow = dateDow[date];
    const dt  = new Date(date+"T00:00:00");
    const el  = document.createElement('span');
    el.className   = 'day-chip'+(selDates.has(date)?' on':'');
    el.dataset.date = date;
    el.textContent  = ABBR[dow]+' '+(dt.getMonth()+1)+'/'+dt.getDate();
    el.onclick = () => {
      selDates.has(date) ? selDates.delete(date) : selDates.add(date);
      syncChips(); apply();
    };
    box.appendChild(el);
  });
}
function syncChips(){
  document.querySelectorAll('.day-chip').forEach(c => c.classList.toggle('on', selDates.has(c.dataset.date)));
}
buildChips('dayChipsMob');
buildChips('dayChipsDsk');

// ==============================
// Time dropdowns
// ==============================
function fillTimes(id){
  let html='';
  for(let m=5*60; m<=21*60; m+=30){
    const v=String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');
    html+='<option value="'+v+'">'+fmtTime(v)+'</option>';
  }
  document.getElementById(id).innerHTML=html;
}
['tStartMob','tEndMob','tStartDsk','tEndDsk'].forEach(fillTimes);
document.getElementById('tStartMob').value = selStart;
document.getElementById('tEndMob').value   = selEnd;
document.getElementById('tStartDsk').value = selStart;
document.getElementById('tEndDsk').value   = selEnd;

function wireTime(src, mirror, setter){
  document.getElementById(src).addEventListener('change', function(){
    setter(this.value);
    document.getElementById(mirror).value = this.value;
    apply();
  });
}
wireTime('tStartMob','tStartDsk', v=>selStart=v);
wireTime('tStartDsk','tStartMob', v=>selStart=v);
wireTime('tEndMob',  'tEndDsk',   v=>selEnd=v);
wireTime('tEndDsk',  'tEndMob',   v=>selEnd=v);

// ==============================
// Segmented controls
// ==============================
function buildSeg(id, opts, getVal, setVal){
  const el = document.getElementById(id);
  el.innerHTML = '';
  opts.forEach(o => {
    const b = document.createElement('button');
    b.className   = 'seg-btn'+(getVal()===o.v?' on':'');
    b.textContent = o.l;
    b.dataset.v   = String(o.v);
    b.onclick = () => {
      setVal(o.v==='any'||isNaN(o.v) ? o.v : Number(o.v));
      syncSegs(); apply();
    };
    el.appendChild(b);
  });
}
function syncSegs(){
  document.querySelectorAll('#playerSegMob .seg-btn, #playerSegDsk .seg-btn').forEach(b => {
    b.classList.toggle('on', Number(b.dataset.v)===selPlayers);
  });
  document.querySelectorAll('#holeSegMob .seg-btn, #holeSegDsk .seg-btn').forEach(b => {
    const bv = b.dataset.v==='any' ? 'any' : Number(b.dataset.v);
    b.classList.toggle('on', bv===selHoles);
  });
}
buildSeg('playerSegMob', PLAYER_OPTS, ()=>selPlayers, v=>selPlayers=v);
buildSeg('playerSegDsk', PLAYER_OPTS, ()=>selPlayers, v=>selPlayers=v);
buildSeg('holeSegMob',   HOLE_OPTS,   ()=>selHoles,   v=>selHoles=v);
buildSeg('holeSegDsk',   HOLE_OPTS,   ()=>selHoles,   v=>selHoles=v);

// ==============================
// Course list — desktop (inline checkboxes)
// ==============================
function buildCourseListDsk(){
  const el = document.getElementById('courseListDsk');
  el.innerHTML = '';
  COURSES.forEach(co => {
    const row = document.createElement('div');
    row.className = 'course-item';
    row.innerHTML = '<span class="cbox'+(selCourses.has(co)?' on':'')+'">'+( selCourses.has(co)?'✓':'' )+'</span><span>'+co+'</span>';
    row.onclick = () => {
      selCourses.has(co) ? selCourses.delete(co) : selCourses.add(co);
      syncCourseLists(); apply();
    };
    el.appendChild(row);
  });
}
function syncCourseLists(){
  // Desktop
  document.querySelectorAll('#courseListDsk .course-item').forEach((row,i) => {
    const co  = COURSES[i];
    const on  = selCourses.has(co);
    const box = row.querySelector('.cbox');
    box.className   = 'cbox'+(on?' on':'');
    box.textContent = on?'✓':'';
  });
  // Mobile popover
  document.querySelectorAll('#ddList .course-item').forEach((row,i) => {
    const co  = COURSES[i];
    const on  = selCourses.has(co);
    const box = row.querySelector('.cbox');
    box.className   = 'cbox'+(on?' on':'');
    box.textContent = on?'✓':'';
  });
  // Dropdown button label
  const n = COURSES.length; const s = selCourses.size;
  document.getElementById('ddBtnLabel').textContent =
    s===n ? 'All courses' : s===0 ? 'No courses' : s+' of '+n;
}
document.getElementById('dskAll').onclick  = () => { COURSES.forEach(c=>selCourses.add(c)); syncCourseLists(); apply(); };
document.getElementById('dskNone').onclick = () => { selCourses.clear(); syncCourseLists(); apply(); };
buildCourseListDsk();

// ==============================
// Course popover — mobile
// ==============================
function buildDdList(){
  const el = document.getElementById('ddList');
  el.innerHTML = '';
  COURSES.forEach(co => {
    const row = document.createElement('div');
    row.className = 'course-item';
    row.innerHTML = '<span class="cbox'+(selCourses.has(co)?' on':'')+'">'+( selCourses.has(co)?'✓':'' )+'</span><span>'+co+'</span>';
    row.onclick = () => {
      selCourses.has(co) ? selCourses.delete(co) : selCourses.add(co);
      syncCourseLists(); apply();
    };
    el.appendChild(row);
  });
}
const ddBtn   = document.getElementById('ddBtn');
const ddPanel = document.getElementById('ddPanel');
ddBtn.onclick = e => { e.stopPropagation(); ddPanel.classList.toggle('open'); };
document.addEventListener('click', e => { if(!ddPanel.contains(e.target)&&e.target!==ddBtn) ddPanel.classList.remove('open'); });
document.getElementById('ddAll').onclick  = () => { COURSES.forEach(c=>selCourses.add(c)); syncCourseLists(); apply(); };
document.getElementById('ddNone').onclick = () => { selCourses.clear(); syncCourseLists(); apply(); };
document.getElementById('ddDone').onclick = () => ddPanel.classList.remove('open');
buildDdList();

// ==============================
// Reset
// ==============================
document.getElementById('resetBtn').onclick = () => {
  selDates = new Set();
  sortedDates.forEach(d => { if(DEFAULTS.days.includes(dateDow[d])) selDates.add(d); });
  selStart   = DEFAULTS.start;
  selEnd     = DEFAULTS.end;
  selPlayers = DEFAULTS.players;
  selHoles   = DEFAULTS.holes;
  selCourses = new Set(COURSES);
  ['tStartMob','tStartDsk'].forEach(id => document.getElementById(id).value=selStart);
  ['tEndMob',  'tEndDsk'  ].forEach(id => document.getElementById(id).value=selEnd);
  syncChips(); syncSegs(); syncCourseLists(); apply();
};

// ==============================
// Day-section collapse
// ==============================
function toggleDay(date){
  dayOpen[date] = !dayOpen[date];
  const open = dayOpen[date];
  document.querySelectorAll('[data-day-row="'+date+'"]').forEach(r => r.style.display = open?'':'none');
  const hdr = document.querySelector('[data-day-hdr="'+date+'"]');
  if(hdr) hdr.querySelector('.day-chev').textContent = open?'▾':'▸';
}

// ==============================
// Course-group toggle
// ==============================
function toggleGroup(id){
  const kids = document.querySelectorAll('[data-grp="'+id+'"]');
  const lbl  = document.getElementById('lbl-'+id);
  const open = kids.length && kids[0].style.display!=='none';
  kids.forEach(r => r.style.display = open?'none':'');
  if(lbl) lbl.textContent = (open?'▸':'▾') + lbl.textContent.slice(1);
}

// ==============================
// Filter + render
// ==============================
function apply(){
  const filtered = DATA.filter(d =>
    selDates.has(d.date) &&
    toMin(d.time) >= toMin(selStart) && toMin(d.time) <= toMin(selEnd) &&
    d.spots >= selPlayers &&
    selCourses.has(d.course) &&
    (selHoles==='any' || d.holes===selHoles)
  );
  render(filtered);
}

function render(rows){
  const board = document.getElementById('board');
  const n     = rows.length;
  const cStr  = '<b>'+n+'</b> tee time'+(n===1?'':'s')+' found';
  document.getElementById('countDsk').innerHTML    = cStr;
  document.getElementById('countMobile').innerHTML = cStr;
  board.innerHTML = '';

  if(n===0){
    board.innerHTML =
      '<div class="empty">'+
      '<div class="empty-icon">🌧️</div>'+
      '<div class="empty-title">No tee times in this window</div>'+
      '<div class="empty-sub">Loosen a filter and keep on truckin\'.</div>'+
      '</div>';
    return;
  }

  rows.sort((a,b) =>
    a.date!==b.date ? (a.date<b.date?-1:1) :
    toMin(a.time)!==toMin(b.time) ? toMin(a.time)-toMin(b.time) :
    a.course<b.course ? -1 : 1);

  // Group by date
  const dateOrder = [];
  const byDate    = new Map();
  rows.forEach(r => {
    if(!byDate.has(r.date)){ byDate.set(r.date,[]); dateOrder.push(r.date); }
    byDate.get(r.date).push(r);
  });

  const tbl = document.createElement('table');
  tbl.innerHTML =
    '<thead><tr>'+
    '<th style="width:140px">Time</th>'+
    '<th>Course</th>'+
    '<th class="holes-col c" style="width:80px">Holes</th>'+
    '<th class="r" style="width:100px">Price</th>'+
    '<th class="c" style="width:90px">Open</th>'+
    '<th style="width:170px"></th>'+
    '</tr></thead>';

  let gi = 0;

  dateOrder.forEach(date => {
    const dayRows = byDate.get(date);
    const dow     = dayRows[0].day;

    // Group by course within day
    const courseOrder = [];
    const byCourse    = new Map();
    dayRows.forEach(r => {
      if(!byCourse.has(r.course)){ byCourse.set(r.course,[]); courseOrder.push(r.course); }
      byCourse.get(r.course).push(r);
    });

    const tbody = document.createElement('tbody');

    // Day header row
    const hTr = document.createElement('tr');
    hTr.className = 'day-head';
    hTr.setAttribute('data-day-hdr', date);
    hTr.onclick = () => toggleDay(date);
    hTr.innerHTML =
      '<td colspan="6"><div class="day-inner">'+
      '<span class="day-label">'+ABBR[dow]+' · '+prettyDate(date)+'</span>'+
      '<span class="day-meta">'+
        '<span>'+dayRows.length+' time'+(dayRows.length===1?'':'s')+'</span>'+
        '<span class="day-chev">▾</span>'+
      '</span>'+
      '</div></td>';
    tbody.appendChild(hTr);

    // Rows grouped by course
    courseOrder.forEach(course => {
      const grp   = byCourse.get(course);
      const first = grp[0];

      if(grp.length===1){
        const r  = grp[0];
        const tr = document.createElement('tr');
        tr.setAttribute('data-day-row', date);
        tr.innerHTML =
          '<td class="time-cell">'+fmtTime(r.time)+'</td>'+
          '<td>'+r.course+'</td>'+
          '<td class="holes-col tc">'+r.holes+'</td>'+
          '<td class="price-cell tr">'+fmtPrice(r.price)+'</td>'+
          '<td class="tc"><span class="spots-pill">'+r.spots+'</span></td>'+
          '<td class="tr"><a class="btn-book" href="'+r.url+'" target="_blank" rel="noopener">Book ›</a></td>';
        tbody.appendChild(tr);

      } else {
        const id  = 'g'+gi++;
        const t0  = fmtTime(grp[0].time);
        const t1  = fmtTime(grp[grp.length-1].time);
        const prices  = grp.map(r=>r.price).filter(p=>p!=null);
        const lo  = prices.length ? Math.round(Math.min(...prices)) : null;
        const hi  = prices.length ? Math.round(Math.max(...prices)) : null;
        const priceStr = prices.length===0?'—':lo===hi?'$'+lo:'$'+lo+'–$'+hi;
        const maxSpots = Math.max(...grp.map(r=>r.spots));

        // Summary row — book link visible immediately, expand toggle beside it
        const sTr = document.createElement('tr');
        sTr.className = 'group-head';
        sTr.setAttribute('data-day-row', date);
        sTr.innerHTML =
          '<td class="group-time">'+t0+' – '+t1+'</td>'+
          '<td>'+first.course+'</td>'+
          '<td class="holes-col tc">'+first.holes+'</td>'+
          '<td class="price-cell tr">'+priceStr+'</td>'+
          '<td class="tc"><span class="spots-pill">'+maxSpots+'</span></td>'+
          '<td class="tr"><div class="group-actions">'+
            '<a class="btn-book" href="'+first.url+'" target="_blank" rel="noopener">Book ›</a>'+
            '<span class="expand-lbl" id="lbl-'+id+'" onclick="toggleGroup(\''+id+'\')">▸ '+grp.length+' times</span>'+
          '</div></td>';
        tbody.appendChild(sTr);

        // Child rows (collapsed by default)
        grp.forEach(r => {
          const cTr = document.createElement('tr');
          cTr.className = 'group-child';
          cTr.setAttribute('data-grp', id);
          cTr.setAttribute('data-day-row', date);
          cTr.style.display = 'none';
          cTr.innerHTML =
            '<td class="child-time">'+fmtTime(r.time)+'</td>'+
            '<td></td>'+
            '<td class="holes-col"></td>'+
            '<td class="price-cell tr">'+fmtPrice(r.price)+'</td>'+
            '<td class="tc"><span class="spots-pill">'+r.spots+'</span></td>'+
            '<td class="tr"><a class="btn-book" href="'+r.url+'" target="_blank" rel="noopener">Book ›</a></td>';
          tbody.appendChild(cTr);
        });
      }
    });

    tbl.appendChild(tbody);
  });

  board.appendChild(tbl);
}

apply();

// ==============================
// Live refresh button (calls the server to re-fetch tee times)
// ==============================
const refreshBtn = document.getElementById('refreshBtn');
if (refreshBtn) {
  refreshBtn.addEventListener('click', async () => {
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Refreshing…';
    try {
      const res = await fetch('/refresh', { method: 'POST' });
      if (!res.ok) throw new Error('refresh failed');
      // The fetch runs in the background server-side (can take 40-60s) --
      // poll /status until it's done, then reload to show fresh data.
      const poll = setInterval(async () => {
        const s = await fetch('/status').then(r => r.json()).catch(() => null);
        if (s && !s.refreshing) {
          clearInterval(poll);
          location.reload();
        }
      }, 3000);
    } catch (e) {
      refreshBtn.disabled = false;
      refreshBtn.textContent = '↻ Refresh';
      alert('Refresh failed — try again in a moment.');
    }
  });
}
</script>
</body>
</html>"""
