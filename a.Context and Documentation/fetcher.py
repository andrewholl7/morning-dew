# ==========================================================================
# fetcher.py  --  Talks to the booking platforms and returns tee times.
# ==========================================================================
#
# Each booking platform (ForeUp, Club Prophet, teeitup) speaks a different
# "language". So we have one *adapter* per platform. Every adapter does the
# same job: given a course + a date, return a list of tee times in ONE common
# shape (see `normalize_foreup` below for the shape). That way the rest of the
# program (filter / dashboard / email) never has to know or care which
# platform a tee time came from.
#
# Only the ForeUp adapter is built right now. The other two raise a clear
# "not implemented yet" so nothing fails silently.
# --------------------------------------------------------------------------

from datetime import datetime, timezone, timedelta
import requests

# Tee times from teeitup come back in UTC; we show them in the course's local
# (Eastern) time. zoneinfo handles daylight saving correctly when the tz
# database is available (it is in Anaconda); otherwise we fall back to a fixed
# EDT offset, which is fine for a 14-day window that doesn't cross a DST flip.
try:
    from zoneinfo import ZoneInfo
    _EASTERN = ZoneInfo("America/New_York")
except Exception:
    _EASTERN = None

# A normal browser-ish User-Agent. Public API, but some servers reject
# requests that look like bots with no User-Agent.
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
}

# How long to wait on a single request before giving up (seconds).
_TIMEOUT = 20


# --------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# --------------------------------------------------------------------------
def fetch_course_day(course, date_str, players, holes):
    """Fetch tee times for one course on one date.

    `date_str` is "YYYY-MM-DD". Returns a list of normalized tee-time dicts
    (possibly empty). Never raises for an "empty day" -- only raises/logs for
    real network or platform errors, which main.py catches per-course.
    """
    platform = course.get("platform")

    if platform == "foreup":
        return _fetch_foreup(course, date_str, players, holes)
    if platform == "teeitup":
        return _fetch_teeitup(course, date_str, players, holes)
    if platform == "chronogolf":
        return _fetch_chronogolf(course, date_str, players, holes)

    # --- Future platforms: adapters not written yet --------------------
    if platform == "cps":
        raise NotImplementedError(
            f"{course['name']}: cps.golf is Cloudflare-protected; not scraped."
        )

    raise ValueError(f"{course['name']}: unknown platform '{platform}'.")


# --------------------------------------------------------------------------
# FOREUP ADAPTER
# --------------------------------------------------------------------------
_FOREUP_TIMES_URL = "https://foreupsoftware.com/index.php/api/booking/times"


def _fetch_foreup(course, date_str, players, holes):
    """Call the public ForeUp booking-times API for one course/date."""
    # ForeUp wants the date as MM-DD-YYYY.
    api_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%m-%d-%Y")

    params = {
        "time": "all",
        "date": api_date,
        "holes": holes,
        "players": players,
        "booking_class": course.get("booking_class", ""),
        "schedule_id": course["schedule_id"],
        "api_key": "no_limits",
    }

    resp = requests.get(
        _FOREUP_TIMES_URL, params=params, headers=_HEADERS, timeout=_TIMEOUT
    )
    resp.raise_for_status()

    data = resp.json()

    # ForeUp returns either a JSON array of tee-time objects, or (when there
    # are none / an issue) something that isn't a list. Treat non-lists as
    # "no times".
    if not isinstance(data, list):
        return []

    booking_url = (
        f"https://foreupsoftware.com/index.php/booking/"
        f"{course['course_id']}/{course['schedule_id']}#teetimes"
    )

    times = []
    for raw in data:
        try:
            times.append(normalize_foreup(raw, course, booking_url))
        except (KeyError, ValueError, TypeError):
            # One malformed record shouldn't sink the whole course.
            continue
    return times


def normalize_foreup(raw, course, booking_url):
    """Convert one raw ForeUp record into our common tee-time shape.

    This common shape is the contract every adapter must produce:

        {
          "course":      "Fort Mill Golf Club",
          "key":         "fortmill",
          "date":        "2026-06-20",        # YYYY-MM-DD
          "time":        "07:30",             # HH:MM, 24-hour
          "day_of_week": "Saturday",
          "holes":       18,
          "spots":       4,                   # open spots in this slot
          "price":       45.0,                # green fee (per player), or None
          "booking_url": "https://...",
          "platform":    "foreup",
          "id":          "fortmill|2026-06-20 07:30|18",   # stable, for dedupe
        }
    """
    # ForeUp's "time" looks like "2026-06-20 07:30".
    dt = datetime.strptime(raw["time"], "%Y-%m-%d %H:%M")

    date = dt.strftime("%Y-%m-%d")
    hhmm = dt.strftime("%H:%M")

    holes = int(raw.get("holes") or 0)
    spots = int(raw.get("available_spots") or 0)

    price = raw.get("green_fee")
    try:
        price = float(price) if price not in (None, "") else None
    except (ValueError, TypeError):
        price = None

    return {
        "course": course["name"],
        "key": course["key"],
        "date": date,
        "time": hhmm,
        "day_of_week": dt.strftime("%A"),
        "holes": holes,
        "spots": spots,
        "price": price,
        "booking_url": booking_url,
        "platform": "foreup",
        # Stable identity for a slot: same course+datetime+holes = same slot,
        # regardless of how many spots are open. Used to avoid re-alerting.
        "id": f"{course['key']}|{date} {hhmm}|{holes}",
    }


# --------------------------------------------------------------------------
# TEEITUP / GOLFNOW ADAPTER  (Kenna backend)
# --------------------------------------------------------------------------
# The course's branded teeitup site asks this API for times. No auth token --
# the course is identified by the `x-be-alias` header (the course's alias).
_KENNA_TIMES_URL = "https://phx-api-be-east-1b.kenna.io/v2/tee-times"


def _fetch_teeitup(course, date_str, players, holes):
    """Call the teeitup/Kenna tee-times API for one course/date.

    Kenna wants the date as YYYY-MM-DD (same as our internal format) and the
    course alias in the x-be-alias header. `players` is ignored -- the API
    returns all slots and we read open spots from each one.

    Some aliases (e.g. Mecklenburg County's "multicourse-booking-engine")
    are shared across several physical courses -- every teetime carries a
    `courseId` identifying which one. If the config entry sets
    `course_id_filter`, only teetimes with a matching courseId are kept;
    otherwise (the normal case -- one alias per course) nothing is filtered.
    """
    headers = {**_HEADERS, "x-be-alias": course["alias"]}
    resp = requests.get(
        _KENNA_TIMES_URL, params={"date": date_str}, headers=headers, timeout=_TIMEOUT
    )
    resp.raise_for_status()

    data = resp.json()
    if not isinstance(data, list):
        return []

    course_id_filter = course.get("course_id_filter")

    times = []
    for day in data:
        for raw in day.get("teetimes", []):
            if course_id_filter and raw.get("courseId") != course_id_filter:
                continue
            try:
                rec = normalize_teeitup(raw, course, holes)
            except (KeyError, ValueError, TypeError):
                continue
            if rec:
                times.append(rec)
    return times


def _teeitup_rate_cents(rate):
    """Best estimate of what a golfer actually pays for this rate, in cents.

    GolfNow "Hot Deal" / trade rates carry an inflated SENTINEL in greenFee*
    (e.g. 50000 = a fake $500 list price); the real price lives in the amount
    due online or in the promotion block. Prepaid/standard rates instead have
    dueOnline*==0 and a genuine greenFee*. So we prefer (1) the amount due
    online, then (2) the promotion price, then (3) the green fee -- and ignore
    any value large enough to obviously be a sentinel.
    """
    SENTINEL = 30000  # > $300 at these municipal courses = not a real fee
    # 1) amount actually due online (hot deals)
    for k in ("dueOnlineRiding", "dueOnlineWalking"):
        v = rate.get(k)
        if isinstance(v, (int, float)) and 0 < v < SENTINEL:
            return v
    # 2) promotion block (the discounted fee)
    promo = rate.get("promotion") or {}
    for k in ("dueOnlineRiding", "dueOnlineWalking", "greenFeeCart", "greenFeeWalking"):
        v = promo.get(k)
        if isinstance(v, (int, float)) and 0 < v < SENTINEL:
            return v
    # 3) standard / prepaid green fee
    for k in ("greenFeeCart", "greenFeeWalking", "greenFee18", "greenFee"):
        v = rate.get(k)
        if isinstance(v, (int, float)) and 0 < v < SENTINEL:
            return v
    return None


def _utc_to_eastern(iso_utc):
    """'2026-06-20T19:10:00.000Z' (UTC) -> datetime in Eastern time."""
    dt = datetime.strptime(iso_utc[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    if _EASTERN is not None:
        return dt.astimezone(_EASTERN)
    return dt.astimezone(timezone(timedelta(hours=-4)))  # EDT fallback


def normalize_teeitup(raw, course, want_holes):
    """Convert one Kenna tee-time into our common shape (see normalize_foreup).

    Returns None for slots we don't want (back-nine starts, or no rate that
    matches the requested hole count).
    """
    if raw.get("backNine"):
        return None  # skip 10th-tee starts; we want a normal front-nine round

    rates = raw.get("rates", []) or []
    # Keep only real-golf rates for the holes we want (exclude simulator bays,
    # which some courses -- e.g. The 500 Club -- list tagged as 18 holes).
    holes_rates = [r for r in rates
                   if r.get("holes") == want_holes and not r.get("isSimulator")]
    if not holes_rates:
        return None

    # Open spots = course capacity for the slot minus who's already booked.
    spots = int(raw.get("maxPlayers") or 0) - int(raw.get("bookedPlayers") or 0)
    spots = max(spots, 0)

    # Price = lowest real price among matching rates (Kenna stores cents).
    fees = [c for c in (_teeitup_rate_cents(r) for r in holes_rates) if c is not None]
    price = round(min(fees) / 100.0, 2) if fees else None

    dt = _utc_to_eastern(raw["teetime"])
    date = dt.strftime("%Y-%m-%d")
    hhmm = dt.strftime("%H:%M")

    return {
        "course": course["name"],
        "key": course["key"],
        "date": date,
        "time": hhmm,
        "day_of_week": dt.strftime("%A"),
        "holes": want_holes,
        "spots": spots,
        "price": price,
        "booking_url": course.get("booking_url", ""),
        "platform": "teeitup",
        "id": f"{course['key']}|{date} {hhmm}|{want_holes}",
    }


# --------------------------------------------------------------------------
# CHRONOGOLF / LIGHTSPEED ADAPTER
# --------------------------------------------------------------------------
# Needs the club_id and a player type (affiliation_type_id). Times are already
# in the club's local time, so no timezone conversion. Chronogolf only tells
# us open vs full (out_of_capacity) -- not how many spots remain -- so we
# report 4 spots for an open slot and 0 for a full one (see config note).
_CHRONOGOLF_TIMES_URL = "https://www.chronogolf.com/marketplace/clubs/{club_id}/teetimes"


def _fetch_chronogolf(course, date_str, players, holes):
    """Call the Chronogolf tee-times API for one course/date."""
    url = _CHRONOGOLF_TIMES_URL.format(club_id=course["club_id"])
    params = {
        "date": date_str,            # YYYY-MM-DD
        "nb_holes": holes,
        # The bracketed key makes requests send affiliation_type_ids[]=<id>,
        # which is the array form the API requires.
        "affiliation_type_ids[]": course["affiliation_type_id"],
    }
    resp = requests.get(url, params=params, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()

    data = resp.json()
    if not isinstance(data, list):
        return []

    times = []
    seen = set()
    for raw in data:
        try:
            rec = normalize_chronogolf(raw, course, holes)
        except (KeyError, ValueError, TypeError):
            continue
        # A club can list the same start time more than once; keep one.
        if rec and rec["id"] not in seen:
            seen.add(rec["id"])
            times.append(rec)

    # Some Chronogolf slots return no green_fees (course hides price on empty
    # tee times). Fill nulls from the day's most common price -- rates are
    # consistent within a day so this is a reliable fallback.
    known = [t["price"] for t in times if t["price"] is not None]
    if known:
        typical = max(set(known), key=known.count)
        for t in times:
            if t["price"] is None:
                t["price"] = typical

    return times


def normalize_chronogolf(raw, course, want_holes):
    """Convert one Chronogolf tee-time into our common shape."""
    date = raw["date"]                 # YYYY-MM-DD
    hhmm = raw["start_time"][:5]       # "HH:MM" (already local time)
    dt = datetime.strptime(f"{date} {hhmm}", "%Y-%m-%d %H:%M")

    # Chronogolf reports only open vs full, not remaining spots.
    spots = 0 if raw.get("out_of_capacity") else 4

    # Price = lowest green fee among the rate options (already in dollars).
    fees = []
    for gf in raw.get("green_fees", []) or []:
        v = gf.get("green_fee", gf.get("price"))
        if isinstance(v, (int, float)) and v > 0:
            fees.append(v)
    price = round(min(fees), 2) if fees else None

    return {
        "course": course["name"],
        "key": course["key"],
        "date": date,
        "time": hhmm,
        "day_of_week": dt.strftime("%A"),
        "holes": want_holes,
        "spots": spots,
        "price": price,
        "booking_url": course.get("booking_url", ""),
        "platform": "chronogolf",
        "id": f"{course['key']}|{date} {hhmm}|{want_holes}",
    }
