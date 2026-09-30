"""Tests for the pure parsing logic of the Yr API client."""
from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

PKG_DIR = Path(__file__).parent.parent / "custom_components" / "yr_summary"

if "yr_summary" not in sys.modules:
    _pkg = types.ModuleType("yr_summary")
    _pkg.__path__ = [str(PKG_DIR)]
    sys.modules["yr_summary"] = _pkg

yr_api = importlib.import_module("yr_summary.yr_api")

Location = yr_api.Location
YrApiError = yr_api.YrApiError


def test_parse_suggest():
    data = {
        "_embedded": {
            "location": [
                {
                    "id": "1-211102",
                    "name": "Trondheim",
                    "urlPath": "Norge/Tr\u00f8ndelag/Trondheim/Trondheim",
                },
                {
                    "id": "5-68090",
                    "name": "Trondheim",
                    "urlPath": "Sverige/Tr\u00f8ndelag/Trondheim",
                },
            ]
        }
    }
    locations = yr_api.parse_suggest(data)
    assert [loc.location_id for loc in locations] == ["1-211102", "5-68090"]
    assert locations[0].display_name == "Trondheim, Norge"
    assert locations[1].display_name == "Trondheim, Sverige"


def test_parse_suggest_empty():
    assert yr_api.parse_suggest({"_embedded": {"location": []}}) == []
    assert yr_api.parse_suggest({}) == []


def test_parse_location():
    location = yr_api.parse_location(
        {"id": "1-211102", "name": "Trondheim",
         "urlPath": "Norge/Tr\u00f8ndelag/Trondheim/Trondheim"}
    )
    assert location == Location(
        location_id="1-211102", name="Trondheim", country="Norge"
    )


def test_parse_suggest_extracts_description_fields():
    data = {
        "_embedded": {
            "location": [
                {
                    "category": {"id": "CK51", "name": "Boligfelt"},
                    "id": "1-2826705",
                    "name": "Dalg\u00e5rd",
                    "elevation": 148,
                    "urlPath": "Norge/Tr\u00f8ndelag/Trondheim/Dalg\u00e5rd",
                    "country": {"id": "NO", "name": "Norge"},
                    "region": {"id": "NO/50", "name": "Tr\u00f8ndelag"},
                    "subregion": {"id": "NO/50/5001", "name": "Trondheim"},
                }
            ]
        }
    }
    (location,) = yr_api.parse_suggest(data)
    assert location.category == "Boligfelt"
    assert location.region == "Tr\u00f8ndelag"
    assert location.subregion == "Trondheim"
    assert location.elevation == 148
    assert location.description == "Boligfelt, Trondheim (Tr\u00f8ndelag), 148 m"


def test_location_description_without_optional_fields():
    assert Location("1-211102", "Trondheim").description is None
    assert (
        Location("1-211102", "Trondheim", region="Tr\u00f8ndelag",
                 elevation=10).description
        == "Tr\u00f8ndelag, 10 m"
    )


def test_location_display_name_omits_redundant_country():
    assert (
        Location("1-211102", "Trondheim", country="Trondheim").display_name
        == "Trondheim"
    )


def test_parse_autotext_ok():
    data = {
        "updated": "2026-09-30T23:42:38+02:00",
        "text": "Det blir klarv\u00e6r i natt og i morgen.",
        "status": {"code": "Ok"},
    }
    result = yr_api.parse_autotext(data)
    assert result["text"] == "Det blir klarv\u00e6r i natt og i morgen."
    assert result["updated"] == "2026-09-30T23:42:38+02:00"


@pytest.mark.parametrize(
    "data",
    [
        {"text": "x", "status": {"code": "Error"}},
        {"text": "", "status": {"code": "Ok"}},
        {"status": {"code": "Ok"}},
        {},
    ],
)
def test_parse_autotext_bad_status(data):
    with pytest.raises(YrApiError):
        yr_api.parse_autotext(data)
