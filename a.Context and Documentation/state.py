# ==========================================================================
# state.py  --  Remembers what we already alerted on, so we don't spam you.
# ==========================================================================
#
# We keep a tiny JSON file (seen_times.json) listing the IDs of the matching
# tee times from the PREVIOUS run. On each run:
#
#   new matches  =  (matches found now)  minus  (matches seen last run)
#
# Only the "new" ones trigger an email. Then we overwrite the file with the
# current matches, so next run compares against this run.
#
# Why overwrite instead of keep-forever? So that if a slot gets booked and
# later re-opens, you get alerted again -- which is exactly what you want.
# --------------------------------------------------------------------------

import json
import os

import config


def load_seen():
    """Return the set of tee-time IDs alerted on last run (empty set if none)."""
    if not os.path.exists(config.STATE_FILE):
        return set()
    try:
        with open(config.STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen_ids", []))
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable file -> treat as a fresh start.
        return set()


def save_seen(match_ids):
    """Overwrite the state file with the IDs that currently match."""
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"seen_ids": sorted(match_ids)}, f, indent=2)
