"""Pure parsing helpers for DoorDash Drive tracking pages (no Home Assistant imports)."""
from __future__ import annotations

import html
import re

CODE_RE = re.compile(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}")
LABELS = {1: "CONFIRMED", 2: "TO THE STORE", 3: "ON THE WAY", 4: "DELIVERED"}

STATE_IDLE = "idle"
STATE_ERROR = "error"

# Unverified against a real page: labels and JSON keys DoorDash might use for
# the drop-off address. Replace with the real ones once a page is captured.
ADDRESS_LABEL_RE = re.compile(
    r"^(?:delivery address|delivering to|deliver to|drop[- ]?off(?: address| location)?)"
    r"\s*[:\-]?\s*(.*)$",
    re.I,
)
ADDRESS_JSON_RE = re.compile(
    r'"(?:printableAddress|formattedAddress|dropoffAddress|deliveryAddress)"\s*:\s*"([^"]{5,200})"'
)


def extract_code(value: str | None) -> str | None:
    """Return the urlCode UUID from a full tracking URL or a bare code."""
    if not value:
        return None
    match = CODE_RE.search(value)
    return match.group(0).lower() if match else None


def tracking_url(code: str) -> str:
    """Build the minimal tracking URL (strips device/consumer IDs)."""
    return f"https://www.doordash.com/orders/drive?urlCode={code}"


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip(" ,")[:200]


def extract_destination(raw: str, segments: list[str]) -> str:
    """Return the drop-off address shown on the page, or "" if none is found.

    Looks for a text node labelled like "Delivery address" (the address is the
    rest of that node or the next one), then for an address field in embedded
    JSON.
    """
    for i, seg in enumerate(segments):
        match = ADDRESS_LABEL_RE.match(seg)
        if not match:
            continue
        rest = match.group(1).strip()
        if rest:
            return _clean(rest)
        if i + 1 < len(segments):
            return _clean(segments[i + 1])
    match = ADDRESS_JSON_RE.search(raw)
    if match:
        try:
            value = match.group(1).encode().decode("unicode_escape")
        except UnicodeDecodeError:
            value = match.group(1)
        return _clean(html.unescape(value))
    return ""


def parse(raw: str) -> dict | None:
    """Parse tracking-page HTML. Returns None if no step indicator is found."""
    text = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    segments = [
        s for s in (re.sub(r"\s+", " ", html.unescape(t)).strip()
                    for t in re.split(r"<[^>]+>", text))
        if s
    ]
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

    return {
        "state": str(step),
        "label": label,
        "detail": detail[:200],
        "eta": eta,
        "destination": extract_destination(raw, segments),
    }
