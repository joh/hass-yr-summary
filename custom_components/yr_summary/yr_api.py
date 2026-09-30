"""Small async client for the public Yr (yr.no) forecast API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientSession, ClientError, ClientResponse

from .const import API_BASE, USER_AGENT


@dataclass(frozen=True)
class Location:
    """A Yr location, e.g. 1-211102 Trondheim."""

    location_id: str
    name: str
    country: str | None = None

    @property
    def display_name(self) -> str:
        if self.country and self.country not in self.name:
            return f"{self.name}, {self.country}"
        return self.name


class YrApiError(Exception):
    """The Yr API request failed or returned an error status."""


def _session_headers() -> dict[str, str]:
    return {"User-Agent": USER_AGENT}


async def _get_json(session: ClientSession, path: str) -> dict[str, Any]:
    url = f"{API_BASE}{path}"
    try:
        async with session.get(url, headers=_session_headers(), timeout=30) as response:
            if response.status != 200:
                raise YrApiError(f"Yr API returned HTTP {response.status}")
            return await response.json()
    except (ClientError, TimeoutError) as err:
        raise YrApiError(f"Could not reach the Yr API: {err}") from err


def _country_from_url_path(url_path: str | None) -> str | None:
    """The first segment of a location's urlPath is the country ('Norge')."""
    if not url_path:
        return None
    first = url_path.split("/", 1)[0]
    return first or None


def parse_suggest(data: dict[str, Any]) -> list[Location]:
    """Parse a /locations/suggest response into Location objects."""
    results = data.get("_embedded", {}).get("location", [])
    return [
        Location(
            location_id=str(item["id"]),
            name=str(item["name"]),
            country=_country_from_url_path(item.get("urlPath")),
        )
        for item in results
    ]


async def async_suggest_locations(session: ClientSession, query: str) -> list[Location]:
    """Search locations by name (as the app's location picker does)."""
    data = await _get_json(session, f"/locations/suggest?q={query}")
    return parse_suggest(data)


def parse_location(data: dict[str, Any]) -> Location:
    """Parse a /locations/{id} response into a Location."""
    return Location(
        location_id=str(data["id"]),
        name=str(data["name"]),
        country=_country_from_url_path(data.get("urlPath")),
    )


async def async_get_location(session: ClientSession, location_id: str) -> Location:
    """Fetch a location by its id (e.g. 1-211102)."""
    data = await _get_json(session, f"/locations/{location_id}")
    return parse_location(data)


def parse_autotext(data: dict[str, Any]) -> dict[str, Any]:
    """Parse an autotext response; raises YrApiError on a bad status."""
    status = data.get("status", {}).get("code", "")
    if status != "Ok" or not data.get("text"):
        raise YrApiError(f"Yr autotext status: {status or 'unknown'}")
    return {"text": data["text"], "updated": data.get("updated")}


async def async_get_autotext(
    session: ClientSession, location_id: str, language: str
) -> dict[str, Any]:
    """Fetch the daily text summary for a location.

    Returns a dict with at least 'text' and 'updated'.
    """
    data = await _get_json(
        session, f"/locations/{location_id}/forecast/autotext?language={language}"
    )
    return parse_autotext(data)
