# Morning Dew — Project Brief

Personal Python tool that monitors public golf booking sites around Charlotte/Fort Mill NC, rebuilds a local HTML dashboard, and sends a Windows notification when new matching tee times appear.

---

## What one run does (`python main.py`)

1. Fetches tee times from every enabled course for the next 14 days
2. Rebuilds `dashboard.html` (open in any browser — all times shown, matches highlighted green)
3. Compares current matches against the previous run; notifies only about *new* ones
4. Saves current matches to `seen_times.json` so next run won't re-alert on the same slots

---

## Courses monitored

| Course | Platform | Status |
|--------|----------|--------|
| Fort Mill Golf Club | ForeUp | ✅ enabled |
| Springfield Golf Club | ForeUp | ✅ enabled |
| Red Bridge Golf Club | ForeUp | ✅ enabled |
| Warrior Golf Club | ForeUp | ✅ enabled |
| Rocky River Golf Club | teeitup/GolfNow | ✅ enabled |
| Eagle Chase Golf Club | teeitup/GolfNow | ✅ enabled |
| Edgewater Golf Club | teeitup/GolfNow | ✅ enabled |
| The 500 Club (Statesville) | teeitup/GolfNow | ✅ enabled |
| Rock Barn Golf & Spa (Jackson) | teeitup/GolfNow | ✅ enabled |
| Kings Mountain Country Club | teeitup/GolfNow (GolfNow Hot Deals only) | ✅ enabled |
| The Tradition Golf Club | Chronogolf | ✅ enabled |
| Waterford Golf Club | Chronogolf | ✅ enabled |
| Carolina Lakes Golf Club | teeitup | ❌ disabled — no public inventory |
| Skybrook Golf Club | Chronogolf | ❌ disabled — Firebase auth + reCAPTCHA |
| Mooresville Golf Course | Chronogolf | ❌ disabled — member-gated |
| Emerald Lake Golf Club | Chronogolf | ❌ disabled — no public inventory |
| Tega Cay Golf Club | CPS/Club Prophet | ❌ disabled — Cloudflare bot protection |

---

## What counts as a match (current defaults in `config.py`)

- **Days:** Saturday, Sunday
- **Time window:** 8:00 AM – 11:00 AM
- **Min open spots:** 4 players
- **Holes:** 18
- **Look-ahead:** 14 days

These defaults also control where the dashboard's filters start when you open the page.

---

## Notifications (`config.py` → `NOTIFY_METHOD`)

| Setting | Behavior |
|---------|----------|
| `"toast"` | Windows desktop pop-up. No setup needed. |
| `"email"` | Gmail. Needs `GMAIL_USER` + `GMAIL_APP_PASSWORD` in `.env`. |
| `"none"` | Silent — dashboard still refreshes. *(current default)* |

---

## Dashboard

- Static HTML file rebuilt every run — open in any browser, no server needed
- Live JS filters: day chips, time-window slider, players dropdown, course selector
- Matching times highlighted green; non-matching times still visible for browsing
- Header shows last-refreshed timestamp

---

## File map

| File | Role |
|------|------|
| `config.py` | **Only file you normally edit** — all courses, criteria, notify method |
| `fetcher.py` | Platform adapters: ForeUp, teeitup/Kenna, Chronogolf |
| `filter.py` | Applies MATCH_DAYS / time window / PLAYERS filter |
| `dashboard.py` | Writes `dashboard.html` |
| `notifier.py` | Windows toast or Gmail alert |
| `state.py` | Loads/saves `seen_times.json` for dedup |
| `main.py` | Runs everything once |
| `requirements.txt` | `requests`, `python-dotenv` — that's it |

---

## Known limitations / future ideas

- **Chronogolf spot counts are approximate** — API only reports open vs. full, not remaining spots. Shows 4 when open, 0 when full.
- **No weekday support yet** — filter.py has a comment showing how to add per-day time windows (e.g. Friday evenings)
- **Run scheduling** — currently manual (`python main.py` or double-click `refresh.bat`). Windows Task Scheduler can automate it.
- **Tega Cay / Skybrook** — can't be added without defeating bot protection; noted in config as permanently disabled
- **No price sorting on dashboard** — times are sorted by course/date/time, not price
