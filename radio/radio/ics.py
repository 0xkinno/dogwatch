"""A calendar file for the booking window. Built from dates computed by the Navigator."""
from __future__ import annotations

import hashlib
from datetime import date, timedelta


def booking_ics(title: str, start: date, end: date, description: str = "") -> bytes:
    uid = hashlib.sha256(f"{title}{start}{end}".encode()).hexdigest()[:16] + "@dogwatch"
    esc = lambda s: s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Dogwatch//Booking window//EN", "BEGIN:VEVENT",
        f"UID:{uid}", f"DTSTAMP:{start.strftime('%Y%m%d')}T000000Z",
        f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{(end + timedelta(days=1)).strftime('%Y%m%d')}",
        f"SUMMARY:{esc(title)}", f"DESCRIPTION:{esc(description)}", "END:VEVENT", "END:VCALENDAR",
    ]
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")
