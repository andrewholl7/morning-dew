# ==========================================================================
# app.py  --  Web wrapper around main.run() for hosting Morning Dew online.
# ==========================================================================
#
# Serves the same dashboard.html that main.py builds, but from a live server
# instead of your PC:
#   - GET  /         -> current dashboard (built on first request if needed)
#   - POST /refresh   -> re-fetches tee times right now, rebuilds the page
#   - A background timer also rebuilds it automatically every REFRESH_MINUTES
#
# Local use is unaffected -- `python main.py` / refresh.bat still work as
# before. This file is only used when deployed (gunicorn app:app).
# --------------------------------------------------------------------------

import os
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, Response

import config
import main

app = Flask(__name__)

_lock = threading.Lock()

REFRESH_MINUTES = 15


def _refresh():
    """Run one fetch+rebuild cycle. Serialized so overlapping triggers
    (the timer and a manual click) can't stomp on the same file."""
    with _lock:
        main.run()


@app.route("/")
def index():
    if not os.path.exists(config.DASHBOARD_FILE):
        _refresh()
    with open(config.DASHBOARD_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    return Response(html, mimetype="text/html")


@app.route("/refresh", methods=["POST"])
def refresh():
    _refresh()
    return {"ok": True}


_scheduler = BackgroundScheduler()
_scheduler.add_job(_refresh, "interval", minutes=REFRESH_MINUTES, id="auto-refresh")
_scheduler.start()

# Build the dashboard once at startup so the first visitor doesn't wait.
threading.Thread(target=_refresh, daemon=True).start()


if __name__ == "__main__":
    # Local dev only -- production uses gunicorn (see Procfile).
    app.run(host="0.0.0.0", port=5000, debug=False)
