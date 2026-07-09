# ==========================================================================
# filter.py  --  Decides which tee times match your criteria.
# ==========================================================================
#
# A tee time "matches" when ALL of these are true:
#   - it's on one of your MATCH_DAYS (e.g. Saturday/Sunday)
#   - its time is inside your window (e.g. 07:00-11:00)
#   - it has enough open spots for your party (>= PLAYERS)
#
# Matches drive both the green highlighting on the dashboard and the email
# alerts. Non-matching times still show on the dashboard, just not highlighted.
# --------------------------------------------------------------------------

import config


def _to_minutes(hhmm):
    """'07:30' -> 450 (minutes since midnight). Makes time comparison easy."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def matches_criteria(tee):
    """Return True if a single normalized tee-time dict matches your criteria."""
    if tee["day_of_week"] not in config.MATCH_DAYS:
        return False

    start = _to_minutes(config.MATCH_TIME_START)
    end = _to_minutes(config.MATCH_TIME_END)
    if not (start <= _to_minutes(tee["time"]) <= end):
        return False

    if tee["spots"] < config.PLAYERS:
        return False

    return True

    # --- Want different time windows per day (e.g. weekday evenings)? -------
    # Replace the single start/end window above with a per-day lookup, e.g.:
    #     WINDOWS = {"Saturday": ("07:00", "11:00"),
    #                "Friday":   ("16:00", "19:00")}
    # then pick the window by tee["day_of_week"]. Left simple for now.


def find_matches(tee_times):
    """Given a list of tee times, return just the ones that match."""
    return [t for t in tee_times if matches_criteria(t)]
