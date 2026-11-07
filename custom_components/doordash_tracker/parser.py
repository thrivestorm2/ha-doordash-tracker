"""Pure parsing helpers for DoorDash Drive tracking pages (no Home Assistant imports)."""
from __future__ import annotations

import html
import re

CODE_RE = re.compile(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}")
LABELS = {1: "CONFIRMED", 2: "TO THE STORE", 3: "ON THE WAY", 4: "DELIVERED"}

STATE_IDLE = "idle"
STATE_ERROR = "error"


def extract_code(value: str | None) -> str | None:
    """Return the urlCode UUID from a full tracking URL or a bare code."""
    if not value:
        return None
    match = CODE_RE.search(value)
    return match.group(0).lower() if match else None


def tracking_url(code: str) -> str:
    """Build the minimal tracking URL (strips device/consumer IDs)."""
    return f"https://www.doordash.com/orders/drive?urlCode={code}"


def parse(raw: str) -> dict | None:
    """Parse tracking-page HTML. Returns None if no step indicator is found."""
    text = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    flat = re.sub(r"\s+", " ", text)

    step_match = re.search(r"Step\s+(\d)\s+out\s+of\s+(\d)", flat)
    if not step_match:
        return None
    step = int(step_match.group(1))
    total = int(step_match.group(2)) or 4
    if total != 4:  # normalize if DoorDash changes the step count
        step = max(1, min(4, round(step * 4 / total)))

    detail_match = re.match(
        r"\s*[:\-]?\s*([A-Z][^.!]{4,150}[.!])", flat[step_match.end():]
    )
    detail = detail_match.group(1).strip() if detail_match else ""
    detail_low = detail.lower()

    label = LABELS.get(step, "DOORDASH")
    if step < 4 and ("arriving" in detail_low or "almost there" in detail_low):
        label = "ARRIVING NOW"
    if "delivered" in detail_low:
        step, label = 4, "DELIVERED"

    eta = ""
    clock = re.search(r"\b(\d{1,2}:\d{2})\s*([AaPp][Mm])\b", flat)
    if clock:
        eta = f"{clock.group(1)} {clock.group(2).upper()}"
    else:
        minutes = re.search(r"\b(\d{1,3})\s*(?:-\s*\d{1,3}\s*)?min", flat, re.I)
        if minutes:
            eta = f"{minutes.group(1)} MIN"

    return {"state": str(step), "label": label, "detail": detail[:200], "eta": eta}
