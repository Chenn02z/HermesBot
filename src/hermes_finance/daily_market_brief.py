"""Deterministic markdown generation for spec 0001."""

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


def generate_daily_market_brief(
    watchlist: list[str], as_of: str, fixture: dict
) -> str:
    """Return a deterministic markdown finance brief."""
    if not isinstance(watchlist, list):
        raise ValueError("watchlist must be a list[str]")
    if not watchlist:
        return _render_validation_failure(as_of, "Watchlist is empty.")

    fixture_data = _validate_fixture(fixture, as_of)
    as_of_dt = fixture_data["as_of_dt"]
    tickers = fixture_data["tickers"]
    invalid_inputs = fixture_data["invalid_inputs"]

    supported: list[str] = []
    duplicates: list[str] = []
    ambiguous: list[tuple[str, str, str]] = []
    unsupported: list[tuple[str, str]] = []
    ordered_sections: list[tuple[str, str, str | None, str | None]] = []
    seen_supported: set[str] = set()

    for raw_symbol in watchlist:
        if not isinstance(raw_symbol, str):
            raise ValueError("watchlist entries must be strings")
        normalized = _normalize_ticker(raw_symbol)
        if normalized in tickers:
            if normalized in seen_supported:
                duplicates.append(normalized)
            else:
                supported.append(normalized)
                seen_supported.add(normalized)
                ordered_sections.append(("supported", normalized, None, None))
            continue
        if normalized in invalid_inputs:
            ambiguous.append((raw_symbol, normalized, invalid_inputs[normalized]))
            ordered_sections.append(
                ("ambiguous", raw_symbol, normalized, invalid_inputs[normalized])
            )
            continue
        unsupported.append((raw_symbol, normalized))
        ordered_sections.append(("unsupported", raw_symbol, normalized, None))

    sections = [
        f"# Daily Market Brief ({fixture_data['as_of']})",
        _render_market_context(
            fixture_data["market_context"],
            as_of_dt,
            fixture_data["market_context_complete"],
        ),
        _render_watchlist_summary(
            watchlist,
            supported,
            duplicates,
            ambiguous,
            unsupported,
        ),
    ]

    for section_type, first, second, third in ordered_sections:
        if section_type == "supported":
            sections.append(_render_supported_ticker(first, tickers[first], as_of_dt))
        elif section_type == "ambiguous":
            assert second is not None and third is not None
            sections.append(_render_ambiguous_section(first, second, third))
        else:
            assert second is not None
            sections.append(_render_unsupported_section(first, second))

    sections.append(_render_limitations())
    report = "\n\n".join(sections).strip() + "\n"
    _assert_report_language(report)
    return report


def _validate_fixture(fixture: dict, as_of: str) -> dict[str, object]:
    if not isinstance(fixture, Mapping):
        raise ValueError("fixture must be a mapping")

    fixture_as_of = fixture.get("as_of")
    if fixture_as_of != as_of:
        raise ValueError("fixture.as_of must match invocation as_of exactly")
    as_of_dt = _parse_iso_datetime(as_of, "as_of")

    market_context = _get_required_mapping(fixture, "market_context")
    indices = _get_required_list(market_context, "indices", "market_context.indices")
    notes = market_context.get("notes", [])
    if not _is_list_like(notes):
        raise ValueError("market_context.notes must be a list when present")

    tickers = _get_required_mapping(fixture, "tickers")
    invalid_inputs = fixture.get("invalid_inputs", {})
    if not isinstance(invalid_inputs, Mapping):
        raise ValueError("invalid_inputs must be an object when present")

    normalized_invalid_inputs: dict[str, str] = {}
    for symbol, reason in invalid_inputs.items():
        if not isinstance(symbol, str) or not isinstance(reason, str):
            raise ValueError("invalid_inputs keys and values must be strings")
        normalized_invalid_inputs[_normalize_ticker(symbol)] = reason

    normalized_tickers: dict[str, Mapping[str, object]] = {}
    for symbol, payload in tickers.items():
        if not isinstance(symbol, str):
            raise ValueError("tickers keys must be strings")
        if not isinstance(payload, Mapping):
            raise ValueError(f"tickers.{symbol} must be an object")
        normalized = _normalize_ticker(symbol)
        if normalized in normalized_invalid_inputs:
            raise ValueError(
                f"ticker {normalized} cannot appear in both tickers and invalid_inputs"
            )
        normalized_tickers[normalized] = payload

    _validate_market_indices(indices)
    _validate_market_notes(notes)
    for symbol, payload in normalized_tickers.items():
        _validate_ticker_shape(symbol, payload)

    return {
        "as_of": fixture_as_of,
        "as_of_dt": as_of_dt,
        "invalid_inputs": normalized_invalid_inputs,
        "market_context": {"indices": list(indices), "notes": list(notes)},
        "market_context_complete": _has_required_market_proxies(indices),
        "tickers": normalized_tickers,
    }


def _validate_market_indices(indices: Sequence[object]) -> None:
    required_fields = (
        "symbol",
        "name",
        "price",
        "change_percent",
        "timestamp",
        "source",
    )
    for index, entry in enumerate(indices):
        path = f"market_context.indices[{index}]"
        if not isinstance(entry, Mapping):
            raise ValueError(f"{path} must be an object")
        for field in required_fields:
            if field not in entry:
                raise ValueError(f"{path}.{field} is required")
        _get_required_number(entry, "price", f"{path}.price")
        _get_required_number(entry, "change_percent", f"{path}.change_percent")
        _parse_iso_datetime(
            _get_required_string(entry, "timestamp", f"{path}.timestamp"),
            f"{path}.timestamp",
        )


def _validate_market_notes(notes: Sequence[object]) -> None:
    for index, note in enumerate(notes):
        path = f"market_context.notes[{index}]"
        if not isinstance(note, Mapping):
            raise ValueError(f"{path} must be an object")
        for field in ("headline", "timestamp", "source"):
            if field not in note:
                raise ValueError(f"{path}.{field} is required")
        _parse_iso_datetime(
            _get_required_string(note, "timestamp", f"{path}.timestamp"),
            f"{path}.timestamp",
        )


def _validate_ticker_shape(symbol: str, payload: Mapping[str, object]) -> None:
    quote = payload.get("quote")
    if quote is not None:
        quote_mapping = _ensure_mapping(quote, f"tickers.{symbol}.quote")
        if "current_price" not in quote_mapping:
            raise ValueError(
                f"tickers.{symbol}.quote.current_price is required when quote exists"
            )
        if "source" not in quote_mapping:
            raise ValueError(
                f"tickers.{symbol}.quote.source is required when quote exists"
            )
        _get_required_number(
            quote_mapping,
            "current_price",
            f"tickers.{symbol}.quote.current_price",
        )
        timestamp = quote_mapping.get("timestamp")
        if timestamp is not None:
            _parse_iso_datetime(
                _get_required_string(
                    quote_mapping,
                    "timestamp",
                    f"tickers.{symbol}.quote.timestamp",
                ),
                f"tickers.{symbol}.quote.timestamp",
            )

    range_data = payload.get("range_20d")
    if range_data is not None:
        range_mapping = _ensure_mapping(range_data, f"tickers.{symbol}.range_20d")
        for field in ("recent_low_20d", "recent_high_20d", "source"):
            if field not in range_mapping:
                raise ValueError(
                    f"tickers.{symbol}.range_20d.{field} is required "
                    "when range_20d exists"
                )
        _get_required_number(
            range_mapping,
            "recent_low_20d",
            f"tickers.{symbol}.range_20d.recent_low_20d",
        )
        _get_required_number(
            range_mapping,
            "recent_high_20d",
            f"tickers.{symbol}.range_20d.recent_high_20d",
        )
        timestamp = range_mapping.get("timestamp")
        if timestamp is not None:
            _parse_iso_datetime(
                _get_required_string(
                    range_mapping,
                    "timestamp",
                    f"tickers.{symbol}.range_20d.timestamp",
                ),
                f"tickers.{symbol}.range_20d.timestamp",
            )

    support_level = payload.get("support_level")
    if support_level is not None:
        support_mapping = _ensure_mapping(
            support_level,
            f"tickers.{symbol}.support_level",
        )
        if "price" not in support_mapping:
            raise ValueError(
                f"tickers.{symbol}.support_level.price is required "
                "when support_level exists"
            )
        _get_required_number(
            support_mapping,
            "price",
            f"tickers.{symbol}.support_level.price",
        )
        timestamp = support_mapping.get("timestamp")
        if timestamp is not None:
            _parse_iso_datetime(
                _get_required_string(
                    support_mapping,
                    "timestamp",
                    f"tickers.{symbol}.support_level.timestamp",
                ),
                f"tickers.{symbol}.support_level.timestamp",
            )

    news = payload.get("news", [])
    if news is None:
        return
    if not _is_list_like(news):
        raise ValueError(f"tickers.{symbol}.news must be a list when present")
    for index, item in enumerate(news):
        path = f"tickers.{symbol}.news[{index}]"
        if not isinstance(item, Mapping):
            raise ValueError(f"{path} must be an object")
        for field in ("headline", "summary", "source"):
            if field not in item:
                raise ValueError(f"{path}.{field} is required")
        timestamp = item.get("timestamp")
        if timestamp is not None:
            _parse_iso_datetime(
                _get_required_string(item, "timestamp", f"{path}.timestamp"),
                f"{path}.timestamp",
            )


def _render_validation_failure(as_of: str, reason: str) -> str:
    parsed_as_of = _parse_iso_datetime(as_of, "as_of")
    return "\n\n".join(
        [
            f"# Daily Market Brief ({parsed_as_of.isoformat()})",
            "## Validation Failure",
            "Deterministic Narrative",
            reason,
            _render_limitations(),
        ]
    ) + "\n"


def _render_market_context(
    market_context: Mapping[str, Sequence[object]],
    as_of_dt: datetime,
    is_complete: bool,
) -> str:
    lines = ["## General Market Context", "Evidence"]
    if is_complete:
        lines.append("Context completeness: complete.")
    else:
        lines.append(
            "Context completeness: incomplete because required S&P 500 and "
            "Nasdaq proxy evidence is missing."
        )

    for entry in market_context["indices"]:
        assert isinstance(entry, Mapping)
        freshness = _freshness_status(
            entry.get("timestamp"),
            as_of_dt,
            QUOTE_FRESHNESS_WINDOW,
        )
        lines.append(
            "- "
            f"{entry['name']} ({entry['symbol']}): price {entry['price']}, "
            f"change {entry['change_percent']}%, timestamp {entry['timestamp']}, "
            f"source {entry['source']}, freshness {freshness}."
        )

    if market_context["notes"]:
        for note in market_context["notes"]:
            assert isinstance(note, Mapping)
            freshness = _news_freshness_status(note.get("timestamp"), as_of_dt)
            lines.append(
                "- Market note: "
                f"{note['headline']}; timestamp {note['timestamp']}, "
                f"source {note['source']}, freshness {freshness}."
            )
    else:
        lines.append("- Optional market notes unavailable.")

    lines.extend(
        [
            "Deterministic Narrative",
            "General market context reflects only supplied fixture evidence and "
            "freshness labels.",
        ]
    )
    return "\n".join(lines)


def _render_watchlist_summary(
    watchlist: list[str],
    supported: list[str],
    duplicates: list[str],
    ambiguous: list[tuple[str, str, str]],
    unsupported: list[tuple[str, str]],
) -> str:
    lines = ["## Watchlist Summary", "Deterministic Narrative"]
    lines.append(f"- Raw inputs: {', '.join(watchlist)}.")
    lines.append(
        "- Supported normalized tickers in report order: "
        f"{', '.join(supported) if supported else 'none'}."
    )
    lines.append(
        "- Duplicate normalized tickers skipped after first occurrence: "
        f"{', '.join(duplicates) if duplicates else 'none'}."
    )
    if ambiguous:
        ambiguous_text = ", ".join(
            f"{normalized} ({reason})" for _, normalized, reason in ambiguous
        )
    else:
        ambiguous_text = "none"
    lines.append(f"- Ambiguous inputs: {ambiguous_text}.")
    if unsupported:
        unsupported_text = ", ".join(normalized for _, normalized in unsupported)
    else:
        unsupported_text = "none"
    lines.append(f"- Unsupported inputs: {unsupported_text}.")
    return "\n".join(lines)


def _render_supported_ticker(
    symbol: str,
    payload: Mapping[str, object],
    as_of_dt: datetime,
) -> str:
    company_name = payload.get("company_name")
    title = f"## {symbol}"
    if isinstance(company_name, str) and company_name.strip():
        title = f"## {symbol} - {company_name}"

    lines = [title, "Evidence"]
    lines.append(_render_quote_line(payload.get("quote"), as_of_dt))
    lines.append(_render_range_line(payload.get("range_20d"), as_of_dt))
    lines.append(_render_support_line(payload.get("support_level"), as_of_dt))
    lines.extend(_render_news(payload.get("news"), as_of_dt))
    lines.extend(_render_pullback_zone(symbol, payload, as_of_dt))
    lines.extend(
        [
            "Deterministic Narrative",
            "This section restates only supplied fixture evidence and "
            "deterministic freshness or zone outcomes.",
        ]
    )
    return "\n".join(lines)


def _render_quote_line(quote: object, as_of_dt: datetime) -> str:
    if not isinstance(quote, Mapping):
        return "- Quote: unavailable."
    timestamp = quote.get("timestamp")
    freshness = _freshness_status(timestamp, as_of_dt, QUOTE_FRESHNESS_WINDOW)
    return (
        "- Quote: "
        f"current_price {quote.get('current_price')}, "
        f"timestamp {timestamp or 'missing'}, "
        f"source {quote.get('source', 'missing')}, "
        f"freshness {freshness}."
    )


def _render_range_line(range_data: object, as_of_dt: datetime) -> str:
    if not isinstance(range_data, Mapping):
        return "- 20-day range: unavailable."
    timestamp = range_data.get("timestamp")
    freshness = _freshness_status(timestamp, as_of_dt, QUOTE_FRESHNESS_WINDOW)
    return (
        "- 20-day range: "
        f"recent_low_20d {range_data.get('recent_low_20d')}, "
        f"recent_high_20d {range_data.get('recent_high_20d')}, "
        f"timestamp {timestamp or 'missing'}, "
        f"source {range_data.get('source', 'missing')}, "
        f"freshness {freshness}."
    )


def _render_support_line(support_level: object, as_of_dt: datetime) -> str:
    if not isinstance(support_level, Mapping):
        return "- Support level: unavailable."
    timestamp = support_level.get("timestamp")
    freshness = _freshness_status(timestamp, as_of_dt, QUOTE_FRESHNESS_WINDOW)
    return (
        "- Support level: "
        f"price {support_level.get('price')}, "
        f"timestamp {timestamp or 'missing'}, "
        f"source {support_level.get('source', 'missing')}, "
        f"freshness {freshness}."
    )


def _render_news(news_items: object, as_of_dt: datetime) -> list[str]:
    if not _is_list_like(news_items) or not news_items:
        return ["- News: unavailable."]

    lines: list[str] = []
    for item in news_items:
        if not isinstance(item, Mapping):
            continue
        freshness = _news_freshness_status(item.get("timestamp"), as_of_dt)
        lines.append(
            "- News item: "
            f"{item.get('headline')}; summary {item.get('summary')}; "
            f"timestamp {item.get('timestamp') or 'missing'}, "
            f"source {item.get('source')}, "
            f"freshness {freshness}."
        )
    return lines or ["- News: unavailable."]


def _render_pullback_zone(
    symbol: str,
    payload: Mapping[str, object],
    as_of_dt: datetime,
) -> list[str]:
    lines = ["### Research-Only Pullback Zone", "Deterministic Calculation"]
    result = _evaluate_pullback_zone(payload, as_of_dt)
    if result["status"] == "evaluated":
        lines.append(
            f"- Candidate zone for {symbol}: "
            f"{result['lower']:.2f} to {result['upper']:.2f}."
        )
        lines.append(
            "- Reference price source: "
            f"{result['reference_source']}; "
            f"reference timestamp {result['reference_timestamp']}."
        )
    else:
        lines.append(f"- Pullback zone not evaluated: {result['reason']}.")
    return lines


def _render_ambiguous_section(raw_symbol: str, normalized: str, reason: str) -> str:
    return "\n".join(
        [
            f"## Ambiguous Input - {normalized}",
            "Evidence",
            f"- Original input: {raw_symbol}.",
            f"- Fixture reason: {reason}.",
            "Deterministic Narrative",
            "The report does not substitute another ticker for an ambiguous input.",
        ]
    )


def _render_unsupported_section(raw_symbol: str, normalized: str) -> str:
    return "\n".join(
        [
            f"## Unsupported Input - {normalized}",
            "Evidence",
            f"- Original input: {raw_symbol}.",
            "- Fixture support: unavailable.",
            "Deterministic Narrative",
            "The report does not invent unsupported ticker evidence.",
        ]
    )


def _render_limitations() -> str:
    return "\n".join(
        [
            "## Limitations",
            LIMITATIONS_SENTENCE,
            "Deterministic Narrative",
            "The report is fixture-backed, template-rendered, and limited to "
            "the supplied evidence.",
        ]
    )


def _evaluate_pullback_zone(
    payload: Mapping[str, object],
    as_of_dt: datetime,
) -> dict[str, object]:
    quote = payload.get("quote")
    if not isinstance(quote, Mapping):
        return {"status": "skipped", "reason": "quote evidence is unavailable"}

    range_data = payload.get("range_20d")
    if not isinstance(range_data, Mapping):
        return {
            "status": "skipped",
            "reason": "20-day range evidence is unavailable",
        }

    current_price = quote.get("current_price")
    recent_low = range_data.get("recent_low_20d")
    recent_high = range_data.get("recent_high_20d")
    if current_price is None or recent_low is None or recent_high is None:
        return {
            "status": "skipped",
            "reason": "required pullback fields are missing",
        }

    quote_status = _freshness_status(
        quote.get("timestamp"),
        as_of_dt,
        QUOTE_FRESHNESS_WINDOW,
    )
    if quote_status != "fresh":
        return {"status": "skipped", "reason": f"quote evidence is {quote_status}"}

    range_status = _freshness_status(
        range_data.get("timestamp"),
        as_of_dt,
        QUOTE_FRESHNESS_WINDOW,
    )
    if range_status != "fresh":
        return {
            "status": "skipped",
            "reason": f"20-day range evidence is {range_status}",
        }

    reference_price = float(recent_low)
    reference_source = "range_20d.recent_low_20d"
    reference_timestamp = range_data.get("timestamp")

    support_level = payload.get("support_level")
    if isinstance(support_level, Mapping):
        support_price = support_level.get("price")
        support_status = _freshness_status(
            support_level.get("timestamp"),
            as_of_dt,
            QUOTE_FRESHNESS_WINDOW,
        )
        if support_price is not None and support_status == "fresh":
            reference_price = float(support_price)
            reference_source = "support_level.price"
            reference_timestamp = support_level.get("timestamp")

    lower = round(reference_price, 2)
    upper = round(reference_price * 1.03, 2)
    if upper >= float(current_price):
        return {
            "status": "skipped",
            "reason": "candidate zone upper bound is greater than or equal to "
            "current price",
        }

    return {
        "status": "evaluated",
        "lower": lower,
        "upper": upper,
        "reference_source": reference_source,
        "reference_timestamp": reference_timestamp,
    }


def _freshness_status(
    timestamp: object,
    as_of_dt: datetime,
    window: timedelta,
) -> str:
    if timestamp is None:
        return "stale"
    parsed = _parse_iso_datetime(str(timestamp), "timestamp")
    if parsed > as_of_dt:
        return "invalid_future"
    if as_of_dt - parsed <= window:
        return "fresh"
    return "stale"


def _news_freshness_status(timestamp: object, as_of_dt: datetime) -> str:
    if timestamp is None:
        return "stale"
    parsed = _parse_iso_datetime(str(timestamp), "timestamp")
    if parsed > as_of_dt:
        return "invalid_future"
    age_days = (as_of_dt.date() - parsed.date()).days
    if age_days <= NEWS_FRESHNESS_WINDOW_DAYS:
        return "fresh"
    return "stale"


def _has_required_market_proxies(indices: Sequence[object]) -> bool:
    has_sp500 = False
    has_nasdaq = False
    for entry in indices:
        if not isinstance(entry, Mapping):
            continue
        symbol = _normalize_ticker(str(entry.get("symbol", "")))
        name = str(entry.get("name", "")).upper()
        if symbol in {"SPY", "^GSPC"} or "S&P 500" in name:
            has_sp500 = True
        if symbol in {"QQQ", "^IXIC"} or "NASDAQ" in name:
            has_nasdaq = True
    return has_sp500 and has_nasdaq


def _normalize_ticker(value: str) -> str:
    return value.strip().upper()


def _parse_iso_datetime(value: str, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO-8601 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone offset")
    return parsed


def _get_required_mapping(
    mapping: Mapping[str, object],
    field: str,
) -> Mapping[str, object]:
    if field not in mapping:
        raise ValueError(f"{field} is required")
    return _ensure_mapping(mapping[field], field)


def _ensure_mapping(value: object, field_name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be an object")
    return value


def _get_required_list(
    mapping: Mapping[str, object],
    field: str,
    field_name: str,
) -> Sequence[object]:
    if field not in mapping:
        raise ValueError(f"{field_name} is required")
    value = mapping[field]
    if not _is_list_like(value):
        raise ValueError(f"{field_name} must be a list")
    return value


def _get_required_string(
    mapping: Mapping[str, object],
    field: str,
    field_name: str,
) -> str:
    value = mapping.get(field)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def _get_required_number(
    mapping: Mapping[str, object],
    field: str,
    field_name: str,
) -> float:
    value = mapping.get(field)
    if not isinstance(value, Real) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number")
    return float(value)


def _is_list_like(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _assert_report_language(report: str) -> None:
    lower_report = report.lower()
    for phrase in PROHIBITED_OUTPUT_PHRASES:
        if phrase in lower_report:
            raise AssertionError(
                f"prohibited phrase found in report output: {phrase}"
            )
