from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from numbers import Real

LIMITATIONS_SENTENCE = (
    "Research only. Not personalized financial advice, not a recommendation to buy "
    "or sell, and not a trade instruction."
)
QUOTE_FRESHNESS_WINDOW = timedelta(hours=36)
NEWS_FRESHNESS_WINDOW_DAYS = 7
PROHIBITED_OUTPUT_PHRASES = (
    "buy zone",
    "target price",
    "upside",
    "should buy",
    "buy now",
    "place an order",
    "execute",
    "position sizing",
    "guarantees",
    "trade instructions",
)


def freshness_status(
    timestamp: object,
    as_of_dt: datetime,
    window: timedelta,
) -> str:
    if timestamp is None:
        return "stale"
    parsed = parse_iso_datetime(str(timestamp), "timestamp")
    if parsed > as_of_dt:
        return "invalid_future"
    if as_of_dt - parsed <= window:
        return "fresh"
    return "stale"


def news_freshness_status(timestamp: object, as_of_dt: datetime) -> str:
    if timestamp is None:
        return "stale"
    parsed = parse_iso_datetime(str(timestamp), "timestamp")
    if parsed > as_of_dt:
        return "invalid_future"
    age_days = (as_of_dt.date() - parsed.date()).days
    if age_days <= NEWS_FRESHNESS_WINDOW_DAYS:
        return "fresh"
    return "stale"


def has_required_market_proxies(indices: Sequence[object]) -> bool:
    has_sp500 = False
    has_nasdaq = False
    for entry in indices:
        if not isinstance(entry, Mapping):
            continue
        symbol = normalize_ticker(str(entry.get("symbol", "")))
        name = str(entry.get("name", "")).upper()
        if symbol in {"SPY", "^GSPC"} or "S&P 500" in name:
            has_sp500 = True
        if symbol in {"QQQ", "^IXIC"} or "NASDAQ" in name:
            has_nasdaq = True
    return has_sp500 and has_nasdaq


def normalize_ticker(value: str) -> str:
    return value.strip().upper()


def parse_iso_datetime(value: str, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO-8601 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone offset")
    return parsed


def get_required_mapping(
    mapping: Mapping[str, object],
    field: str,
) -> Mapping[str, object]:
    if field not in mapping:
        raise ValueError(f"{field} is required")
    return ensure_mapping(mapping[field], field)


def ensure_mapping(value: object, field_name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object")
    return value


def get_required_list(
    mapping: Mapping[str, object],
    field: str,
    field_name: str,
) -> Sequence[object]:
    if field not in mapping:
        raise ValueError(f"{field_name} is required")
    value = mapping[field]
    if not is_list_like(value):
        raise ValueError(f"{field_name} must be a list")
    return value


def get_required_string(
    mapping: Mapping[str, object],
    field: str,
    field_name: str,
) -> str:
    value = mapping.get(field)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def get_required_number(
    mapping: Mapping[str, object],
    field: str,
    field_name: str,
) -> float:
    value = mapping.get(field)
    if not isinstance(value, Real) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number")
    return float(value)


def is_list_like(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def assert_report_language(report: str) -> None:
    lower_report = report.lower()
    for phrase in PROHIBITED_OUTPUT_PHRASES:
        if phrase in lower_report:
            raise AssertionError(
                f"prohibited phrase found in report output: {phrase}"
            )
