# Yr Summary for Home Assistant

Shows the official [Yr](https://www.yr.no) daily text summary ("Kort fortalt")
for a location as a sensor in Home Assistant, e.g.:

> Det blir klarvær i natt og i morgen.

The text is fetched from Yr's own forecast API (`www.yr.no/api/v0`), the same
API the Yr app uses. No API key is required.

Available in **Bokmål, Nynorsk, English, Svenska and Dansk**.

## Features

- `sensor.yr_summary` — state is the daily Yr text summary
- Attributes: `location`, `language`, `updated` (when Yr last refreshed the text)
- Set up from the UI (config flow): type a location name (or a location id
  like `1-211102`) and pick the language
- Multiple locations / languages can be configured as separate entries

## Installation

Install with [HACS](https://hacs.xyz), or clone this repository into
`<config dir>/custom_components/yr_summary`.

## Notes

- Polling interval defaults to 30 minutes. The Yr text itself is updated by
  Yr a few times a day; the `updated` attribute tells you when it last changed.
- Data © [Yr](https://www.yr.no), a joint service by NRK and the Norwegian
  Meteorological Institute. This integration only reads the public API that
  the official app uses.
