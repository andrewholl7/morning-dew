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
        "holes":   "any",
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
  html, body { overflow-x:hidden; max-width:100%; }
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
    display:flex; align-items:center; justify-content:space-between; gap:10px;
  }
  .brand { display:flex; align-items:center; gap:11px; min-width:0; }
  .wordmark {
    font-family:'Bricolage Grotesque',sans-serif; font-size:26px;
    font-weight:600; color:var(--navy); letter-spacing:-.5px;
  }
  .syf { width:44px; height:44px; flex:none; display:block; filter:drop-shadow(0 1px 3px #0003); }
  .refreshed-wrap { display:flex; align-items:center; gap:12px; flex:none; }
  .refreshed { font-size:12px; font-weight:600; color:#56708a; white-space:nowrap; }
  .btn-refresh {
    cursor:pointer; border:1.5px solid var(--sky-b);
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
  .frow-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }

  /* Day chips */
  .chips { display:flex; gap:5px; flex-wrap:wrap; }
  .day-chip {
    cursor:pointer; user-select:none; border-radius:999px; padding:7px 13px;
    font:700 12.5px/1 'Hanken Grotesk'; background:#fff;
    border:1.5px solid var(--border); color:var(--muted); transition:.12s;
  }
  .day-chip.on { background:var(--sky); border-color:var(--sky-b); color:var(--day-text); }

  /* Time range slider */
  .range-slider { position:relative; height:28px; margin:4px 0 2px; }
  .range-track {
    position:absolute; top:50%; left:0; right:0; height:4px; margin-top:-2px;
    background:var(--border); border-radius:2px;
  }
  .range-fill {
    position:absolute; top:50%; height:4px; margin-top:-2px;
    background:var(--carolina); border-radius:2px;
  }
  .range-input {
    position:absolute; top:0; left:0; width:100%; height:28px; margin:0;
    background:transparent; pointer-events:none;
    -webkit-appearance:none; appearance:none;
  }
  .range-input::-webkit-slider-runnable-track { -webkit-appearance:none; background:transparent; height:28px; }
  .range-input::-webkit-slider-thumb {
    -webkit-appearance:none; pointer-events:auto; width:22px; height:22px; border-radius:50%;
    background:#fff; border:2.5px solid var(--carolina); box-shadow:0 2px 6px rgba(20,30,55,.25);
    cursor:pointer; margin-top:0;
  }
  .range-input::-moz-range-track { background:transparent; height:28px; border:none; }
  .range-input::-moz-range-thumb {
    pointer-events:auto; width:22px; height:22px; border-radius:50%;
    background:#fff; border:2.5px solid var(--carolina); box-shadow:0 2px 6px rgba(20,30,55,.25);
    cursor:pointer;
  }
  .range-labels {
    display:flex; justify-content:space-between;
    font:700 12.5px/1 'Hanken Grotesk'; color:var(--navy);
  }

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
    padding:8px; width:min(320px,90vw); box-shadow:0 16px 40px rgba(20,30,55,.22);
  }
  .dd-panel.open { display:block; }
  .dd-quick { display:flex; gap:8px; margin-bottom:8px; }
  .dd-quick button {
    flex:1; cursor:pointer; border:1px solid var(--border); border-radius:8px;
    background:#f3eddf; font:700 12px/1 'Hanken Grotesk'; color:var(--navy); padding:8px;
  }
  .dd-list { max-height:240px; overflow-y:auto; }
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
  button.btn-book { border:none; cursor:pointer; }

  /* Time-picker modal */
  .modal-overlay {
    display:none; position:fixed; inset:0; background:rgba(20,30,55,.5);
    z-index:200; align-items:center; justify-content:center; padding:16px;
  }
  .modal-overlay.open { display:flex; }
  .modal-box {
    background:#fff; border-radius:14px; width:min(340px,100%); max-height:75vh;
    overflow-y:auto; box-shadow:0 20px 50px rgba(20,30,55,.3);
  }
  .modal-head {
    position:sticky; top:0; background:#fff; display:flex; align-items:center;
    justify-content:space-between; padding:10px 14px; border-bottom:1px solid var(--border);
  }
  .modal-head span { font-family:'Bricolage Grotesque',sans-serif; font-weight:600; font-size:13.5px; color:var(--navy); }
  .modal-close { cursor:pointer; border:none; background:none; font-size:14px; color:var(--muted); padding:4px; line-height:1; }
  .modal-list { padding:4px 8px; }
  .modal-row {
    display:flex; align-items:center; justify-content:space-between; gap:8px;
    padding:8px 6px; border-bottom:1px solid var(--row-b);
  }
  .modal-row:last-child { border-bottom:none; }
  .modal-time { font-weight:700; color:var(--navy); font-size:13px; flex:0 0 auto; }
  .modal-meta { display:flex; align-items:center; gap:6px; font-size:11.5px; color:var(--muted); flex:0 0 auto; }
  .modal-row .btn-book { padding:5px 9px; font-size:11px; }

  /* Empty state */
  .empty { text-align:center; padding:64px 30px; }
  .empty-icon  { font-size:28px; margin-bottom:10px; }
  .empty-title { font-family:'Bricolage Grotesque',sans-serif; font-size:19px; font-weight:600; color:var(--navy); }
  .empty-sub   { font-size:13.5px; color:#7c8aa0; margin-top:6px; }

  /* ---- Responsive ---- */
  @media (max-width:700px) {
    .hbar         { flex-wrap:wrap; padding:10px 14px; gap:6px 10px; }
    .wordmark     { font-size:19px; }
    .syf          { width:32px; height:32px; }
    .refreshed-wrap { flex:1 1 auto; justify-content:flex-end; gap:8px; }
    .refreshed    { font-size:10px; overflow:hidden; text-overflow:ellipsis; max-width:150px; }
    .btn-refresh  { padding:5px 11px; font-size:11px; }
    .rail         { display:none; }
    .filter-card  { display:flex; }
    .layout       { padding:0 0 40px; flex-direction:column; gap:0; }
    .results      { padding:0; }
    .results-head { display:none; }
    .count-mobile { display:block; }
    .card         { border-radius:0; border-left:none; border-right:none; box-shadow:none; }
    th.holes-col, td.holes-col { display:none; }
    .day-chip     { padding:9px 14px; font-size:13px; }
    .seg-btn      { padding:10px 0; }
    .dd-btn       { padding:11px 14px; width:100%; justify-content:space-between; }
    .course-item  { padding:10px 6px; font-size:14px; }
    .range-input::-webkit-slider-thumb { width:26px; height:26px; }
    .range-input::-moz-range-thumb     { width:26px; height:26px; }

    /* Collapse the results table into single-line flex rows so nothing
       ever needs horizontal scrolling to reach the Book button. */
    table        { display:block; width:100%; }
    thead        { display:none; }
    tbody        { display:block; width:100%; }
    tr.day-head  { display:block; }
    tr.day-head td { padding:9px 14px; }
    tbody tr:not(.day-head) {
      display:flex; align-items:center; flex-wrap:nowrap; gap:6px;
      width:100%; padding:8px 12px; border-bottom:1px solid var(--row-b);
    }
    td { padding:0; border:none; font-size:12.5px; }
    td.time-cell, td.group-time { flex:0 0 auto; font-size:11.5px; white-space:nowrap; }
    td:nth-child(2) {
      flex:1 1 auto; min-width:0; font-size:12px; font-weight:600;
      overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
    }
    td.price-cell { flex:0 0 auto; font-size:12px; }
    td.tc         { flex:0 0 auto; }
    .spots-pill   { min-width:18px; padding:2px 7px; font-size:11px; }
    td:last-child { flex:0 0 auto; padding-left:2px; }
    .btn-book     { padding:6px 10px; font-size:11.5px; }
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
    <div class="refreshed-wrap">
      <span class="refreshed">last refreshed __GENERATED__</span>
      <button class="btn-refresh" id="refreshBtn">↻ Refresh</button>
    </div>
  </div>
</header>
<div class="seam"></div>

<!-- ===== Mobile filter card ===== -->
<div class="filter-card">
  <div class="fblock" style="margin:0">
    <div class="frow-head">
      <span class="flabel" style="margin:0">Days</span>
      <span>
        <button class="btn-small" id="dateAllMob">All</button>
        &nbsp;·&nbsp;
        <button class="btn-small" id="dateNoneMob">None</button>
      </span>
    </div>
    <div class="chips" id="dayChipsMob"></div>
  </div>
  <div class="fblock" style="margin:0">
    <span class="flabel">Time window</span>
    <div class="range-slider" id="sliderWrapMob">
      <div class="range-track"></div>
      <div class="range-fill" id="rangeFillMob"></div>
      <input type="range" class="range-input" id="tStartMob" min="300" max="1260" step="30">
      <input type="range" class="range-input" id="tEndMob" min="300" max="1260" step="30">
    </div>
    <div class="range-labels">
      <span id="tStartLabelMob"></span>
      <span id="tEndLabelMob"></span>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="flabel" style="margin:0;width:54px;flex:none;">Holes</span>
    <div class="seg" id="holeSegMob" style="flex:1"></div>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="flabel" style="margin:0;width:54px;flex:none;">Players</span>
    <div class="seg" id="playerSegMob" style="flex:1"></div>
  </div>
  <div class="fblock" style="margin:0">
    <span class="flabel">Courses</span>
    <div class="dd">
      <button class="dd-btn" id="ddBtn" type="button">
        <span id="ddBtnLabel">All courses</span>
        <span style="color:var(--muted);font-size:10px;">▾</span>
      </button>
      <div class="dd-panel" id="ddPanel">
        <div class="dd-quick">
          <button id="ddAll">All</button>
          <button id="ddNone">None</button>
        </div>
        <div class="dd-list" id="ddList"></div>
        <div class="dd-footer">
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
      <div class="frow-head">
        <span class="flabel" style="margin:0">Days</span>
        <span>
          <button class="btn-small" id="dateAllDsk">All</button>
          &nbsp;·&nbsp;
          <button class="btn-small" id="dateNoneDsk">None</button>
        </span>
      </div>
      <div class="chips" id="dayChipsDsk"></div>
    </div>
    <div class="fblock">
      <span class="flabel">Time window</span>
      <div class="range-slider" id="sliderWrapDsk">
        <div class="range-track"></div>
        <div class="range-fill" id="rangeFillDsk"></div>
        <input type="range" class="range-input" id="tStartDsk" min="300" max="1260" step="30">
        <input type="range" class="range-input" id="tEndDsk" min="300" max="1260" step="30">
      </div>
      <div class="range-labels">
        <span id="tStartLabelDsk"></span>
        <span id="tEndLabelDsk"></span>
      </div>
    </div>
    <div class="fblock">
      <span class="flabel">Holes</span>
      <div class="seg" id="holeSegDsk"></div>
    </div>
    <div class="fblock">
      <span class="flabel">Players</span>
      <div class="seg" id="playerSegDsk"></div>
    </div>
    <div class="fblock">
      <div class="frow-head">
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

<!-- ===== Time-picker modal (grouped tee times) ===== -->
<div class="modal-overlay" id="modalOverlay">
  <div class="modal-box">
    <div class="modal-head">
      <span id="modalTitle"></span>
      <button class="modal-close" id="modalClose" type="button">✕</button>
    </div>
    <div class="modal-list" id="modalList"></div>
  </div>
</div>

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

function selectAllDates(){ selDates = new Set(sortedDates); syncChips(); apply(); }
function selectNoneDates(){ selDates = new Set(); syncChips(); apply(); }
document.getElementById('dateAllMob').onclick  = selectAllDates;
document.getElementById('dateNoneMob').onclick = selectNoneDates;
document.getElementById('dateAllDsk').onclick  = selectAllDates;
document.getElementById('dateNoneDsk').onclick = selectNoneDates;

// ==============================
// Time range slider
// ==============================
const TIME_MIN = 5*60, TIME_MAX = 21*60;
const fromMin  = m => String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');

function paintSlider(sfx){
  const s = toMin(selStart), e = toMin(selEnd);
  const pct = v => (v-TIME_MIN)/(TIME_MAX-TIME_MIN)*100;
  document.getElementById('tStart'+sfx).value = s;
  document.getElementById('tEnd'+sfx).value   = e;
  document.getElementById('rangeFill'+sfx).style.left  = pct(s)+'%';
  document.getElementById('rangeFill'+sfx).style.right = (100-pct(e))+'%';
  document.getElementById('tStartLabel'+sfx).textContent = fmtTime(selStart);
  document.getElementById('tEndLabel'+sfx).textContent   = fmtTime(selEnd);
}
function paintAllSliders(){ paintSlider('Mob'); paintSlider('Dsk'); }

function wireSlider(sfx){
  document.getElementById('tStart'+sfx).addEventListener('input', function(){
    let v = Number(this.value);
    if(v > toMin(selEnd)) v = toMin(selEnd);
    selStart = fromMin(v);
    paintAllSliders(); apply();
  });
  document.getElementById('tEnd'+sfx).addEventListener('input', function(){
    let v = Number(this.value);
    if(v < toMin(selStart)) v = toMin(selStart);
    selEnd = fromMin(v);
    paintAllSliders(); apply();
  });
}
['Mob','Dsk'].forEach(wireSlider);
paintAllSliders();

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
  paintAllSliders();
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
// Time-picker modal (grouped tee times)
// ==============================
const groupStore   = {};
const modalOverlay = document.getElementById('modalOverlay');
const modalTitle   = document.getElementById('modalTitle');
const modalList    = document.getElementById('modalList');

function openModal(id){
  const g = groupStore[id];
  if(!g) return;
  modalTitle.textContent = g.course+' · '+ABBR[g.dow]+' '+prettyDate(g.date);
  modalList.innerHTML = g.rows.map(r =>
    '<div class="modal-row">'+
      '<span class="modal-time">'+fmtTime(r.time)+'</span>'+
      '<span class="modal-meta"><span>'+fmtPrice(r.price)+'</span><span class="spots-pill">'+r.spots+'</span></span>'+
      '<a class="btn-book" href="'+r.url+'" target="_blank" rel="noopener">Book ›</a>'+
    '</div>'
  ).join('');
  modalOverlay.classList.add('open');
}
function closeModal(){ modalOverlay.classList.remove('open'); }
document.getElementById('modalClose').onclick = closeModal;
modalOverlay.addEventListener('click', e => { if(e.target===modalOverlay) closeModal(); });

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
  Object.keys(groupStore).forEach(k => delete groupStore[k]);

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

        // Summary row — clicking Book opens a modal to pick a specific time
        groupStore[id] = { course: first.course, date, dow, rows: grp };
        const sTr = document.createElement('tr');
        sTr.className = 'group-head';
        sTr.setAttribute('data-day-row', date);
        sTr.innerHTML =
          '<td class="group-time">'+t0+' – '+t1+'</td>'+
          '<td>'+first.course+'</td>'+
          '<td class="holes-col tc">'+first.holes+'</td>'+
          '<td class="price-cell tr">'+priceStr+'</td>'+
          '<td class="tc"><span class="spots-pill">'+maxSpots+'</span></td>'+
          '<td class="tr"><button class="btn-book" type="button" onclick="openModal(\''+id+'\')">'+grp.length+' times ›</button></td>';
        tbody.appendChild(sTr);
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
