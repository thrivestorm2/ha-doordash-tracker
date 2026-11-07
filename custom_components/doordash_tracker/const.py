"""Constants for DoorDash Tracker."""
from datetime import timedelta

DOMAIN = "doordash_tracker"

POLL_INTERVAL = timedelta(seconds=60)
TERMINAL_HOLD = timedelta(minutes=10)  # keep "delivered"/"error" visible, then reset
MAX_TRACK_TIME = timedelta(hours=2)    # hard stop for a forgotten link

USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
)
