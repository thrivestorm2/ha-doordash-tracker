"""Polling coordinator for DoorDash Tracker."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MAX_TRACK_TIME, POLL_INTERVAL, TERMINAL_HOLD, USER_AGENT
from .parser import STATE_ERROR, STATE_IDLE, extract_code, parse, tracking_url

_LOGGER = logging.getLogger(__name__)

IDLE = {"state": STATE_IDLE, "label": "", "detail": "", "eta": "", "destination": ""}


class DoorDashCoordinator(DataUpdateCoordinator[dict]):
    """Fetches the tracking page while a URL is set; idles otherwise."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=POLL_INTERVAL,
        )
        self.url_value: str = ""
        self.url_code: str | None = None
        self.started: datetime | None = None
        self._terminal_since: datetime | None = None

    def set_url(self, value: str) -> None:
        """Set (or clear) the tracking link."""
        code = extract_code(value)
        self.url_value = value if code else ""
        self.url_code = code
        self.started = dt_util.utcnow() if code else None
        self._terminal_since = None

    def _clear(self) -> dict:
        self.set_url("")
        return dict(IDLE)

    async def _async_update_data(self) -> dict:
        if not self.url_code:
            return dict(IDLE)

        now = dt_util.utcnow()
        if self.started and now - self.started > MAX_TRACK_TIME:
            _LOGGER.debug("Max tracking time reached; clearing link")
            return self._clear()

        result = await self._fetch(self.url_code)

        if result["state"] in ("4", STATE_ERROR):
            if self._terminal_since is None:
                self._terminal_since = now
            elif now - self._terminal_since > TERMINAL_HOLD:
                _LOGGER.debug("Terminal state held %s; clearing link", TERMINAL_HOLD)
                return self._clear()
        else:
            self._terminal_since = None

        return result

    async def _fetch(self, code: str) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                tracking_url(code),
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return {**IDLE, "state": STATE_ERROR, "detail": f"HTTP {resp.status}"}
                raw = await resp.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            return {**IDLE, "state": STATE_ERROR, "detail": f"fetch failed: {err}"}

        parsed = parse(raw)
        if parsed is None:
            return {
                **IDLE,
                "state": STATE_ERROR,
                "detail": "no step found (expired link or bot check)",
            }
        return parsed
