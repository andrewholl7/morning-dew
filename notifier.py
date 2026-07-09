# ==========================================================================
# notifier.py  --  Tells you about NEW matching tee times.
# ==========================================================================
#
# How you're notified is set by config.NOTIFY_METHOD:
#   "toast" -> a Windows desktop pop-up (default). No setup, no accounts.
#   "email" -> Gmail (needs GMAIL_USER + GMAIL_APP_PASSWORD in .env).
#   "none"  -> don't notify (the dashboard still refreshes).
#
# The toast uses the Windows notification API through PowerShell, so there's
# nothing to pip-install. It appears whenever you're logged in -- which is
# also exactly when the every-2-hours scheduled run fires.
# --------------------------------------------------------------------------

import base64
import os
import smtplib
import ssl
import subprocess
from email.message import EmailMessage

import config

_ABBR = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed", "Thursday": "Thu",
         "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}


# --------------------------------------------------------------------------
# PUBLIC ENTRY POINT
# --------------------------------------------------------------------------
def send_new_times(new_matches):
    """Notify about newly-available matching tee times via the chosen method.

    Returns True if a notification was sent, False if skipped.
    """
    if not new_matches:
        return False

    method = getattr(config, "NOTIFY_METHOD", "toast")
    if method == "toast":
        return _send_toast(new_matches)
    if method == "email":
        return _send_email(new_matches)
    if method == "none":
        return False

    print(f"  Unknown NOTIFY_METHOD '{method}' -- not notifying.")
    return False


# --------------------------------------------------------------------------
# WINDOWS TOAST
# --------------------------------------------------------------------------
def _send_toast(matches):
    """Pop a native Windows notification listing the new tee times."""
    title = f"⛳ {config.APP_NAME}: {len(matches)} new tee time(s)"

    ordered = _sorted(matches)
    lines = [_toast_line(m) for m in ordered[:4]]
    if len(ordered) > 4:
        lines.append(f"+{len(ordered) - 4} more")
    body = "\n".join(lines)

    try:
        _show_toast(title, body)
        print(f"  Toast shown ({len(matches)} new time(s)).")
        return True
    except Exception as e:
        print(f"  Could not show toast: {e}")
        return False


def _toast_line(m):
    return f"{m['course']} - {_ABBR.get(m['day_of_week'], '')} {_md(m['date'])} {_fmt_12h(m['time'])}"


def _show_toast(title, body):
    """Show a toast via the built-in Windows API (PowerShell, no installs)."""
    xml = (
        "<toast><visual><binding template='ToastGeneric'>"
        f"<text>{_xml(title)}</text><text>{_xml(body)}</text>"
        "</binding></visual></toast>"
    )
    b64 = base64.b64encode(xml.encode("utf-8")).decode("ascii")
    # Use PowerShell's own registered App ID so the toast reliably displays.
    app_id = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe"
    ps = (
        "$x=[System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('" + b64 + "'));"
        "$null=[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime];"
        "$null=[Windows.Data.Xml.Dom.XmlDocument,Windows.Data,ContentType=WindowsRuntime];"
        "$d=New-Object Windows.Data.Xml.Dom.XmlDocument;$d.LoadXml($x);"
        "$t=[Windows.UI.Notifications.ToastNotification]::new($d);"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('" + app_id + "').Show($t);"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
        creationflags=0x08000000,  # CREATE_NO_WINDOW -- never flash a console
        timeout=20,
        check=True,
    )


# --------------------------------------------------------------------------
# EMAIL (Gmail) -- used when NOTIFY_METHOD = "email"
# --------------------------------------------------------------------------
_SMTP_HOST = "smtp.gmail.com"
_SMTP_PORT = 465  # SSL


def _send_email(matches):
    user = os.getenv("GMAIL_USER")
    pw = os.getenv("GMAIL_APP_PASSWORD")
    to = config.NOTIFY_TO or user
    if not user or not pw:
        print(
            "  Gmail credentials not found in environment -- not sending.\n"
            "  Set GMAIL_USER and GMAIL_APP_PASSWORD in your .env file."
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = f"\U0001f339 {config.APP_NAME}: {len(matches)} new tee time(s)"
    msg["From"] = user
    msg["To"] = to
    msg.set_content(_plain_body(matches))
    msg.add_alternative(_html_body(matches), subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(_SMTP_HOST, _SMTP_PORT, context=context) as server:
        server.login(user, pw)
        server.send_message(msg)
    print(f"  Email sent to {to} ({len(matches)} new time(s)).")
    return True


# --------------------------------------------------------------------------
# Formatting helpers
# --------------------------------------------------------------------------
def _fmt_price(price):
    return f"${price:.0f}" if price is not None else "n/a"


def _fmt_12h(hhmm):
    h, m = (int(x) for x in hhmm.split(":"))
    ap = "AM" if h < 12 else "PM"
    hh = h % 12 or 12
    return f"{hh}:{m:02d} {ap}"


def _md(date):
    _, mo, d = date.split("-")
    return f"{int(mo)}/{int(d)}"


def _xml(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _sorted(matches):
    return sorted(matches, key=lambda m: (m["date"], m["time"], m["course"]))


def _plain_body(matches):
    lines = ["New matching tee times:\n"]
    for m in _sorted(matches):
        lines.append(
            f"- {m['course']}: {m['day_of_week']} {m['date']} at {m['time']} "
            f"| {m['holes']} holes | {m['spots']} spots | {_fmt_price(m['price'])}\n"
            f"  Book: {m['booking_url']}"
        )
    return "\n".join(lines)


def _html_body(matches):
    rows = []
    for m in _sorted(matches):
        rows.append(
            "<tr>"
            f"<td>{m['course']}</td>"
            f"<td>{m['day_of_week']} {m['date']}</td>"
            f"<td>{m['time']}</td>"
            f"<td>{m['holes']}</td>"
            f"<td>{m['spots']}</td>"
            f"<td>{_fmt_price(m['price'])}</td>"
            f"<td><a href=\"{m['booking_url']}\">Book</a></td>"
            "</tr>"
        )
    return (
        "<html><body style='font-family:sans-serif'>"
        f"<h2 style='color:#e02434'>{config.APP_NAME} — new tee times</h2>"
        "<table border='1' cellpadding='6' cellspacing='0'>"
        "<tr><th>Course</th><th>Date</th><th>Time</th><th>Holes</th>"
        "<th>Spots</th><th>Price</th><th></th></tr>"
        + "".join(rows) +
        "</table></body></html>"
    )
