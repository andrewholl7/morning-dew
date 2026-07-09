# ==========================================================================
# main.py  --  Run the whole thing once. (No internal loop -- run on demand.)
# ==========================================================================
#
# What one run does:
#   1. Work out which dates to check (next N days, weekends only by default).
#   2. Fetch tee times for every enabled course on every date.
#   3. Build/refresh dashboard.html (all times; matches highlighted green).
#   4. Compare matches to last run; email only the NEW ones.
#   5. Save state so the next run knows what's already been seen.
#
# Just run:   python main.py
# --------------------------------------------------------------------------

from datetime import date, timedelta

from dotenv import load_dotenv

import config
import fetcher
import filter as flt
import state
import notifier
from dashboard import build_dashboard

# Load secrets from .env (looked for next to this script) into the environment.
import os
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


def dates_to_check():
    """Return the list of 'YYYY-MM-DD' dates this run should fetch."""
    today = date.today()
    out = []
    for offset in range(config.LOOKAHEAD_DAYS):
        d = today + timedelta(days=offset)
        day_name = d.strftime("%A")
        if config.FETCH_ALL_DAYS or day_name in config.MATCH_DAYS:
            out.append(d.strftime("%Y-%m-%d"))
    return out


def enabled_courses():
    return [c for c in config.COURSES if c.get("enabled")]


def run():
    courses = enabled_courses()
    dates = dates_to_check()

    print("=" * 60)
    print("Tee Time Monitor -- single run")
    print(f"Courses : {', '.join(c['name'] for c in courses)}")
    print(f"Dates   : {len(dates)} day(s) -> {dates[0]} .. {dates[-1]}")
    print("=" * 60)

    # course name -> list of normalized tee times (for the dashboard)
    tees_by_course = {c["name"]: [] for c in courses}
    all_tees = []

    for course in courses:
        found = 0
        # Almost every course is 18 holes (config.HOLES), but a course entry
        # can set its own "holes" (e.g. Sifford is a 9-hole muni course).
        course_holes = course.get("holes", config.HOLES)
        for d in dates:
            try:
                tees = fetcher.fetch_course_day(
                    course, d, config.FETCH_PLAYERS, course_holes
                )
            except Exception as e:  # network hiccup, bad ID, etc. -- keep going
                print(f"  ! {course['name']} {d}: {e}")
                continue
            tees_by_course[course["name"]].extend(tees)
            all_tees.extend(tees)
            found += len(tees)
        print(f"  {course['name']}: {found} available time(s) fetched.")

    # --- Dashboard (always rebuilt, shows everything) ----------------------
    build_dashboard(tees_by_course)
    print(f"\nDashboard written -> {config.DASHBOARD_FILE}")

    # --- Matches + new-since-last-run --------------------------------------
    matches = flt.find_matches(all_tees)
    match_ids = {m["id"] for m in matches}

    seen = state.load_seen()
    new_matches = [m for m in matches if m["id"] not in seen]

    print(f"\nMatches now : {len(matches)}")
    print(f"New vs last : {len(new_matches)}")

    # --- Email only the new ones -------------------------------------------
    if new_matches:
        for m in sorted(new_matches, key=lambda x: (x["date"], x["time"])):
            print(f"   NEW  {m['course']}: {m['day_of_week']} {m['date']} {m['time']}")
        notifier.send_new_times(new_matches)

    # --- Remember this run's matches for next time -------------------------
    state.save_seen(match_ids)
    print("\nDone.")


if __name__ == "__main__":
    run()
