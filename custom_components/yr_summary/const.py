"""Constants for the Yr Summary component."""

DOMAIN = "yr_summary"

CONF_LOCATION_ID = "location_id"
CONF_LOCATION_NAME = "location_name"
CONF_LANGUAGE = "language"
CONF_SCAN_INTERVAL = "scan_interval"  # minutes

DEFAULT_SCAN_INTERVAL_MINUTES = 30
DEFAULT_LANGUAGE = "nb"

LANGUAGES = {
    "nb": "Bokm\u00e5l",
    "nn": "Nynorsk",
    "en": "English",
    "sv": "Svenska",
    "da": "Dansk",
}

API_BASE = "https://www.yr.no/api/v0"
USER_AGENT = "hass-yr-summary/0.1 (https://github.com/joh/hass-yr-summary)"
