# 🌹 Morning Dew

Personal tool that checks public golf-booking sites around Charlotte/Fort Mill
for open tee times, refreshes a Grateful Dead–styled one-page `dashboard.html`,
and pops a **Windows notification** when a **new** time matches your criteria.

The dashboard has live filters (no re-running needed): **date chips, a time
window, a players dropdown, and a course selector.** They open on your defaults
from `config.py` (Sat/Sun, 8–11 AM, 4 players, all courses) — so the page loads
showing exactly what you'd be alerted about. Slide them around to explore
everything else that's open.

Monitors a dozen courses across three booking platforms (ForeUp,
teeitup/GolfNow, Chronogolf). The exact list — plus a few that couldn't be
wired up (behind member logins, reCAPTCHA, or bot protection) — lives in
`config.py`, each with a note explaining why.

## Setup (one time)

1. Install Python 3.11+ (or just use your existing Anaconda Python).
2. Install the two dependencies (Anaconda already has both):
   ```powershell
   pip install -r requirements.txt
   ```
3. **Notifications need no setup** — they're Windows pop-ups by default. To use
   email instead, set `NOTIFY_METHOD = "email"` in `config.py`, then copy
   `.env.example` to `.env` and add your Gmail address + 16-char App Password.

## Refresh — easy mode (double-click)

**Double-click `refresh.bat`.** It checks every course, rebuilds the dashboard,
and opens it in your browser. That's the whole loop — do it whenever you want
fresh times.

> Why a batch file instead of a button on the page? A web page opened from your
> disk isn't allowed to run programs on your computer (browsers block that for
> safety). `refresh.bat` works because Windows runs it directly. The dashboard
> header always shows "last refreshed: ..." so you know how current it is.

## Run it — one-off / scheduled

```powershell
python main.py
```

Each run:
- fetches available times for the next 14 days (all days, so the dashboard's
  day filter has something to show),
- rewrites `dashboard.html` — open it in any browser,
- emails you only the **newly** appeared matching times (no repeats).

## Change what you're looking for

Everything is in **`config.py`** — courses, days, time window, party size,
look-ahead. It's the only file you need to edit.

## How the pieces fit

| File | Job |
|------|-----|
| `config.py` | All your settings (the only file you normally edit) |
| `fetcher.py` | Calls each booking platform, returns times in one common shape |
| `filter.py` | Decides which times match your criteria |
| `dashboard.py` | Writes `dashboard.html` |
| `notifier.py` | Sends the Gmail alert |
| `state.py` | Remembers last run (so you aren't emailed twice) |
| `main.py` | Runs all of the above, once |

## Notes

- Uses the same public booking API the courses' own websites use; no login or
  scraping. Please keep the run frequency reasonable (every 10–15 min is fine).
- `seen_times.json` and `dashboard.html` are generated automatically — don't
  edit them.
