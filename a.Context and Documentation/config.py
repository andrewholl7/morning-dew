# ==========================================================================
# config.py  --  ALL your knobs live here. Edit this file, not the others.
# ==========================================================================
#
# This is the only file a non-engineer needs to touch. Change the courses,
# the days/times you care about, and how many players. Everything else
# (fetching, filtering, emailing, the dashboard) reads its settings from here.
#
# Secrets (Gmail login) do NOT go in this file. They live in the `.env` file
# so they never get shared by accident. See `.env.example`.
# --------------------------------------------------------------------------

# Name shown on the dashboard and in email subjects.
APP_NAME = "Morning Dew"

# --------------------------------------------------------------------------
# 1) COURSES TO MONITOR
# --------------------------------------------------------------------------
# Each course is one entry in this list.
#
# For ForeUp courses you only need two numbers, both found in the course's
# booking page URL:  foreupsoftware.com/index.php/booking/<course_id>/<schedule_id>
#   - course_id   : first number  (only used to build the "Book" link)
#   - schedule_id : second number (this is what the API actually needs)
#
# All three ForeUp courses below were validated against the live API on
# 2026-06-15, so these numbers are real, not placeholders.
#
# `booking_class` can stay "" (empty) -- the API returns public rates that
# way, which is what we want. Leave it empty unless you have a member login.
#
# Set "enabled": False to temporarily stop monitoring a course without
# deleting it.

COURSES = [
    {
        "name": "Fort Mill Golf Club",
        "key": "fortmill",          # short id used internally; keep it unique
        "platform": "foreup",
        "course_id": 20823,
        "schedule_id": 5728,
        "booking_class": "",
        "enabled": True,
    },
    {
        "name": "Springfield Golf Club",
        "key": "springfield",
        "platform": "foreup",
        "course_id": 20825,
        "schedule_id": 5730,
        "booking_class": "",
        "enabled": True,
    },
    {
        "name": "Red Bridge Golf Club",
        "key": "redbridge",
        "platform": "foreup",
        "course_id": 21207,
        "schedule_id": 7256,
        "booking_class": "",
        "enabled": True,
    },
    # Asheboro, NC -- ~65 miles out, outside the usual 30-mile radius, but
    # explicitly requested. Validated live on 2026-07-08 (~40+ slots/day).
    {
        "name": "Tot Hill Farm Golf Club",
        "key": "tothillfarm",
        "platform": "foreup",
        "course_id": 22389,
        "schedule_id": 10640,
        "booking_class": "",
        "enabled": True,
    },
    # Lancaster, SC -- ~46 miles out, outside the usual 30-mile radius, but
    # explicitly requested. Validated live on 2026-07-08.
    {
        "name": "Lancaster Golf Club",
        "key": "lancaster",
        "platform": "foreup",
        "course_id": 20824,
        "schedule_id": 5729,
        "booking_class": "",
        "enabled": True,
    },

    # ----------------------------------------------------------------------
    # teeitup / GolfNow courses (Kenna backend). `alias` is how the API
    # identifies the course (sent as the x-be-alias header). Validated live.
    # ----------------------------------------------------------------------
    {
        "name": "Rocky River Golf Club",
        "key": "rockyriver",
        "platform": "teeitup",
        "alias": "rocky-river-golf-club",
        "booking_url": "https://golf.teeitup.com/54490/",
        "enabled": True,
    },
    {
        "name": "Eagle Chase Golf Club",
        "key": "eaglechase",
        "platform": "teeitup",
        "alias": "eagle-chase-golf-club",
        "booking_url": "https://eagle-chase-golf-club.book.teeitup.com/",
        "enabled": True,
    },
    {
        "name": "Edgewater Golf Club",
        "key": "edgewater",
        "platform": "teeitup",
        "alias": "edgewater-golf-club",
        "booking_url": "https://edgewater-golf-club.book.teeitup.com/",
        "enabled": True,
    },
    {
        # Statesville, NC location (GolfNow). The Phoenix AZ "500 Club" is a
        # different course on Chronogolf -- not this one.
        "name": "The 500 Club",
        "key": "fivehundred",
        "platform": "teeitup",
        "alias": "the-500-club",
        "booking_url": "https://the-500-club.book.teeitup.com/",
        "enabled": True,
    },
    {
        # The public Jackson course at Rock Barn (the Jones course is members
        # only). Found on teeitup with this (long) alias.
        "name": "Rock Barn Golf & Spa (Jackson)",
        "key": "rockbarn",
        "platform": "teeitup",
        "alias": "rock-barn-golf-and-spa-jackson-course",
        "booking_url": "https://rock-barn-golf-and-spa-jackson-course.book.teeitup.com/",
        "enabled": True,
    },
    # Validated live on 2026-07-08 -- real inventory on teeitup/Kenna.
    {
        "name": "Monroe Country Club",
        "key": "monroecc",
        "platform": "teeitup",
        "alias": "monroe-country-club",
        "booking_url": "https://monroe-country-club.book.teeitup.com/",
        "enabled": True,
    },
    # Sifford is one of 4 Mecklenburg County muni courses that share a single
    # teeitup alias ("multicourse-booking-engine") -- every teetime in that
    # feed carries a courseId, so `course_id_filter` picks out just Sifford's
    # (mapped live on 2026-07-08 via its GolfNow facility id, 1563, which
    # matches the "course=1563" param on Sifford's own booking page). It's a
    # 9-hole course, hence "holes": 9 (see main.py's per-course holes override).
    {
        "name": "Dr. Charles L. Sifford Golf Course",
        "key": "sifford",
        "platform": "teeitup",
        "alias": "multicourse-booking-engine",
        "course_id_filter": "54f14bdf0c8ad60378b01891",
        "holes": 9,
        "booking_url": "https://meck-county-golf-booking-engine.book.teeitup.com/teetimes?course=1563",
        "enabled": True,
    },
    # Kings Mountain is RESOLD on GolfNow only -- its native sheet (Chronogolf)
    # publishes nothing, so the ONLY times that exist are GolfNow "Hot Deal"
    # trade times. Those are real but bookable solely via the GolfNow link below
    # (NOT the course's own site), and they sell/expire fast. The name is
    # labelled so a shown time is clearly a GolfNow deal. Disable if unwanted.
    # (Waterford used to be here too, but it's natively on Chronogolf -- moved
    # to the Chronogolf section below so we show its real tee sheet.)
    {
        "name": "Kings Mountain Country Club",
        "key": "kingsmountain",
        "platform": "teeitup",
        "alias": "kings-mountain-country-club",
        "booking_url": "https://www.golfnow.com/tee-times/facility/1729-kings-mountain-country-club/search",
        "enabled": True,
    },
    # Carolina Lakes resolves on teeitup but carries ZERO inventory there (its
    # real tee sheet is on ClubHouse Online). Re-verified live on 2026-07-08,
    # still 0. Disabled -- would need a separate ClubHouse Online adapter to
    # be actually useful.
    {
        "name": "Carolina Lakes Golf Club",
        "key": "carolinalakes",
        "platform": "teeitup",
        "alias": "carolina-lakes-golf-club",
        "booking_url": "https://www.golfnow.com/tee-times/facility/16601-carolina-lakes-golf-club/search",
        "enabled": False,
    },
    # Chester Golf Club (Chester, SC -- ~55 miles out, outside the usual
    # 30-mile radius, but explicitly requested). Resolves on teeitup with a
    # real, live booking page (chester-golf-club.book.teeitup.com), but the
    # alias carries ZERO inventory across every date tried on 2026-07-08.
    # Disabled -- same dead-end pattern as Carolina Lakes above.
    {
        "name": "Chester Golf Club",
        "key": "chester",
        "platform": "teeitup",
        "alias": "chester-golf-club",
        "booking_url": "https://chester-golf-club.book.teeitup.com/",
        "enabled": False,
    },

    # ----------------------------------------------------------------------
    # Chronogolf (Lightspeed). Validated live. Needs club_id + a player type
    # (affiliation_type_id); times come back already in local time.
    # CAVEAT: Chronogolf does NOT report remaining spots -- only open vs full.
    # So "spots" is 4 when a slot is open and 0 when full. An open morning slot
    # is *probably* a free foursome, but a single/pair could have booked it.
    # Treat the spot count for these two as an availability flag, not exact.
    # ----------------------------------------------------------------------
    {
        "name": "The Tradition Golf Club",
        "key": "tradition",
        "platform": "chronogolf",
        "club_id": 9436,
        "affiliation_type_id": 38566,
        "booking_url": "https://www.chronogolf.com/club/the-tradition",
        "enabled": True,
    },
    {
        "name": "Waterford Golf Club",
        "key": "waterford",
        "platform": "chronogolf",
        "club_id": 13044,
        "affiliation_type_id": 52998,
        "booking_url": "https://www.chronogolf.com/club/waterford-golf-club-south-carolina",
        "enabled": True,
    },
    # Matthews, NC. Validated live on 2026-07-08 -- real inventory returned.
    {
        "name": "The Divide Golf Club",
        "key": "thedivide",
        "platform": "chronogolf",
        "club_id": 9419,
        "affiliation_type_id": 38498,
        "booking_url": "https://www.chronogolf.com/club/the-divide",
        "enabled": True,
    },
    # Charlotte, NC. Validated live on 2026-07-08 -- real inventory returned.
    {
        "name": "Highland Creek Golf Club",
        "key": "highlandcreek",
        "platform": "chronogolf",
        "club_id": 18944,
        "affiliation_type_id": 111817,
        "booking_url": "https://www.chronogolf.com/club/highland-creek-golf-club",
        "enabled": True,
    },
    # Warrior books online via ForeUp (course 18999 / schedule 795), NOT its
    # Chronogolf listing (which returns empty). Validated live -- ~40 slots/day.
    {
        "name": "Warrior Golf Club",
        "key": "warrior",
        "platform": "foreup",
        "course_id": 18999,
        "schedule_id": 795,
        "booking_class": "",
        "enabled": True,
    },
    # ----------------------------------------------------------------------
    # Recon'd but NOT scrapeable -- left DISABLED. No open API exposes their
    # public tee times:
    #  - Skybrook: actually books via CourseRev.ai (api.courserev.ai), gated
    #    behind Firebase auth + reCAPTCHA -- not an open GET, and reCAPTCHA
    #    won't be bypassed. (Its Chronogolf club 9385 is member-gated -> 0.)
    #    Would need a browser session capture to even attempt.
    #    Re-verified live on 2026-07-08 -- unchanged, still a dead end.
    #  - Mooresville: municipal; runs its own .aspx tee sheet. Chronogolf
    #    (club 9255) member-gated / empty. Re-verified live on 2026-07-08 --
    #    unchanged, still a dead end.
    # ----------------------------------------------------------------------
    {
        "name": "Skybrook Golf Club",
        "key": "skybrook",
        "platform": "chronogolf",
        "club_id": 9385,
        "affiliation_type_id": 38362,
        "booking_url": "https://skybrookclub.bookings.courserev.ai/tee-times",
        "enabled": False,
    },
    {
        "name": "Mooresville Golf Course",
        "key": "mooresville",
        "platform": "chronogolf",
        "club_id": 9255,
        "affiliation_type_id": 37842,
        "booking_url": "https://www.chronogolf.com/club/mooresville-golf-course",
        "enabled": False,
    },
    # Emerald Lake (Matthews, branded "The Emerald"): Chronogolf club 9105 AND
    # teeitup both return 0 -- no public online inventory found. Re-verified
    # live on 2026-07-08, still 0. Disabled -- would need a working adapter for
    # whatever platform their real tee sheet is on to be actually useful.
    {
        "name": "Emerald Lake Golf Club",
        "key": "emeraldlake",
        "platform": "chronogolf",
        "club_id": 9105,
        "affiliation_type_id": 37242,
        "booking_url": "https://www.chronogolf.com/club/emerald-lake-golf-club",
        "enabled": False,
    },
    # Birkdale Golf Club (Huntersville, NC). Resolves on Chronogolf (club
    # 8994, address-confirmed) but carries ZERO inventory there -- validated
    # live on 2026-07-08 across multiple dates. Disabled -- dead end.
    {
        "name": "Birkdale Golf Club",
        "key": "birkdale",
        "platform": "chronogolf",
        "club_id": 8994,
        "affiliation_type_id": 36798,
        "booking_url": "https://www.chronogolf.com/club/birkdale-golf-club-north-carolina",
        "enabled": False,
    },
    # Olde Sycamore Golf Plantation (Mint Hill/Charlotte, NC). Resolves on
    # Chronogolf (club 9291, listed inactive) but carries ZERO inventory --
    # validated live on 2026-07-08 across multiple dates. Disabled -- dead end.
    {
        "name": "Olde Sycamore Golf Plantation",
        "key": "oldesycamore",
        "platform": "chronogolf",
        "club_id": 9291,
        "affiliation_type_id": 37986,
        "booking_url": "https://www.chronogolf.com/club/olde-sycamore-golf-plantation",
        "enabled": False,
    },
    # Charlotte National Golf Club (Indian Trail, NC). Resolves on Chronogolf
    # (club 9047, listed inactive) but carries ZERO inventory -- validated
    # live on 2026-07-08 across multiple dates. Disabled -- dead end.
    {
        "name": "Charlotte National Golf Club",
        "key": "charlottenational",
        "platform": "chronogolf",
        "club_id": 9047,
        "affiliation_type_id": 37010,
        "booking_url": "https://www.chronogolf.com/club/charlotte-national-golf-course",
        "enabled": False,
    },
    # Crowders Mountain Golf Club (Kings Mountain, NC). Resolves on Chronogolf
    # (club 9080, listed inactive) but carries ZERO inventory -- validated
    # live on 2026-07-08 across multiple dates. Disabled -- dead end.
    {
        "name": "Crowders Mountain Golf Club",
        "key": "crowdersmountain",
        "platform": "chronogolf",
        "club_id": 9080,
        "affiliation_type_id": 37142,
        "booking_url": "https://www.chronogolf.com/club/crowders-mountain-golf-club",
        "enabled": False,
    },

    # ----------------------------------------------------------------------
    # Tega Cay (cps.golf / Club Prophet) sits behind Cloudflare bot protection
    # (scripts get a 403 challenge). Pulling it would mean defeating that,
    # which this tool won't do -- book Tega Cay manually. Left disabled.
    # ----------------------------------------------------------------------
    {
        "name": "Tega Cay Golf Club",
        "key": "tegacay",
        "platform": "cps",
        "enabled": False,
    },
]

# --------------------------------------------------------------------------
# 2) WHAT COUNTS AS A "MATCH" (used for green highlighting + email alerts)
# --------------------------------------------------------------------------

# These also become the DEFAULT positions of the dashboard's interactive
# filters, so the page opens showing exactly what you'd get an email about.

# Days of the week you care about. Full names, capitalized.
# To add weekday evenings later, just add e.g. "Friday" here.
MATCH_DAYS = ["Saturday", "Sunday"]

# Time window, 24-hour clock. 8:00 AM to 11:00 AM = "08:00" to "11:00".
MATCH_TIME_START = "08:00"
MATCH_TIME_END = "11:00"

# Minimum open spots you need. Slots with at least this many spots match.
PLAYERS = 4

# How many days ahead to look, starting today (14 = today through day +13,
# so there are always two full weekends in view).
LOOKAHEAD_DAYS = 14

# Round to play. ForeUp courses here are 18-hole.
HOLES = 18

# Party size sent to the ForeUp API when fetching. This is a server-side
# filter: asking for 4 hides every slot with fewer than 4 open spots, which
# would starve the dashboard's player filter. So we fetch at the broadest
# useful size (2) to pull in 2- and 4-spot slots, then the dashboard's player
# dropdown filters them down. Leave at 2 unless you know what you're doing.
FETCH_PLAYERS = 2

# --------------------------------------------------------------------------
# 3) WHICH DAYS TO ACTUALLY FETCH
# --------------------------------------------------------------------------
# True  = fetch every day in the look-ahead window. Needed so the dashboard's
#         day filter actually has weekday data to show. ~14 days x N courses
#         of API calls per run (fine for personal use every 10-15 min).
# False = fetch only the days in MATCH_DAYS (leaner, but the day filter then
#         only has weekends to toggle between).
FETCH_ALL_DAYS = True

# --------------------------------------------------------------------------
# 4) NOTIFICATIONS -- how you're told about NEW matching tee times
# --------------------------------------------------------------------------
# "toast" = Windows desktop pop-up. No setup, no accounts. Appears when you're
#           logged in to this PC (also when the every-2-hours run fires).
# "email" = Gmail. Needs a 16-char App Password in .env (see .env.example).
# "none"  = don't notify; the dashboard still refreshes every run.
NOTIFY_METHOD = "none"

# Email-only setting (used when NOTIFY_METHOD = "email"). Leave None to send to
# your own address (GMAIL_USER from .env).
NOTIFY_TO = None

# --------------------------------------------------------------------------
# 5) FILE LOCATIONS (you normally don't need to change these)
# --------------------------------------------------------------------------
# Anchored to THIS folder, so the dashboard and state file always land next to
# the scripts -- no matter which directory you happen to run the command from.
import os
_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HERE  = os.path.dirname(os.path.abspath(__file__))

STATE_FILE     = os.path.join(_HERE, "seen_times.json")    # remembers last run
DASHBOARD_FILE = os.path.join(_ROOT, "Live Site.html")     # regenerated each run
