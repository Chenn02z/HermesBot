from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hermes_finance import generate_daily_market_brief

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "finance"
    / "base_fixture.json"
)
AS_OF = "2026-06-26T16:30:00-04:00"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def test_full_report_renders_order_duplicates_and_visible_invalid_inputs() -> None:
    report = generate_daily_market_brief(
        [" nvda ", "BRK.B", "msft", "NVDA", "XYZ"],
        AS_OF,
        load_fixture(),
    )

    assert report.startswith(f"# Daily Market Brief ({AS_OF})")
    assert "## General Market Context" in report
    assert "Context completeness: complete." in report
    assert "Supported normalized tickers in report order: NVDA, MSFT." in report
    assert (
        "Duplicate normalized tickers skipped after first occurrence: NVDA."
        in report
    )
    assert (
        "Ambiguous inputs: BRK.B (Ambiguous class/share formatting in fixture)."
        in report
    )
    assert "Unsupported inputs: XYZ." in report
    assert report.index("## NVDA - NVIDIA Corporation") < report.index(
        "## MSFT - Microsoft Corporation"
    )
    assert "## Ambiguous Input - BRK.B" in report
    assert "## Unsupported Input - XYZ" in report
    assert "### Research-Only Pullback Zone" in report
    assert "Candidate zone for NVDA: 166.00 to 170.98." in report
    assert "Reference price source: support_level.price" in report
    assert (
        "Support level: price 166.0, timestamp 2026-06-26T16:00:00-04:00, "
        "source fixture, freshness fresh."
    ) in report
    assert "## Limitations" in report


def test_visible_input_sections_follow_watchlist_order() -> None:
    report = generate_daily_market_brief(
        ["XYZ", "NVDA", "BRK.B"],
        AS_OF,
        load_fixture(),
    )

    assert report.index("## Unsupported Input - XYZ") < report.index(
        "## NVDA - NVIDIA Corporation"
    )
    assert report.index("## NVDA - NVIDIA Corporation") < report.index(
        "## Ambiguous Input - BRK.B"
    )


def test_empty_watchlist_returns_visible_validation_failure() -> None:
    report = generate_daily_market_brief([], AS_OF, load_fixture())

    assert "## Validation Failure" in report
    assert "Watchlist is empty." in report


def test_missing_news_renders_unavailable_and_stale_news_is_labeled() -> None:
    report = generate_daily_market_brief(["MSFT", "AAPL"], AS_OF, load_fixture())

    assert "## MSFT - Microsoft Corporation" in report
    assert "- News: unavailable." in report
    assert "## AAPL - Apple Inc." in report
    assert "Older Apple headline" in report
    assert "freshness stale" in report


def test_missing_news_timestamp_is_labeled_stale_without_blocking_report() -> None:
    fixture = load_fixture()
    del fixture["tickers"]["NVDA"]["news"][0]["timestamp"]

    report = generate_daily_market_brief(["NVDA"], AS_OF, fixture)

    assert "## NVDA - NVIDIA Corporation" in report
    assert "timestamp missing" in report
    assert "freshness stale" in report
    assert "Candidate zone for NVDA: 166.00 to 170.98." in report


def test_missing_market_proxy_marks_context_incomplete() -> None:
    fixture = load_fixture()
    fixture["market_context"]["indices"] = fixture["market_context"]["indices"][:1]

    report = generate_daily_market_brief(["NVDA"], AS_OF, fixture)

    assert (
        "Context completeness: incomplete because required S&P 500 and Nasdaq "
        "proxy evidence is missing."
    ) in report
    assert "## NVDA - NVIDIA Corporation" in report


def test_missing_ticker_quote_renders_incomplete_and_skips_pullback_zone() -> None:
    fixture = load_fixture()
    del fixture["tickers"]["MSFT"]["quote"]

    report = generate_daily_market_brief(["MSFT"], AS_OF, fixture)

    assert "- Quote: unavailable." in report
    assert "Pullback zone not evaluated: quote evidence is unavailable." in report


def test_stale_quote_and_future_support_timestamp_degrade_visibly() -> None:
    fixture = load_fixture()
    fixture["tickers"]["NVDA"]["quote"]["timestamp"] = "2026-06-24T03:00:00-04:00"
    fixture["tickers"]["TSLA"]["support_level"] = {
        "price": 280.0,
        "timestamp": "2026-06-26T16:45:00-04:00",
        "source": "fixture",
    }

    report = generate_daily_market_brief(["NVDA", "TSLA"], AS_OF, fixture)

    assert "Pullback zone not evaluated: quote evidence is stale." in report
    assert "Support level: price 280.0" in report
    assert "freshness invalid_future" in report
    assert "Candidate zone for TSLA: 295.00 to 303.85." not in report
    assert (
        "Pullback zone not evaluated: candidate zone upper bound is greater "
        "than or equal to current price."
    ) in report


def test_stale_range_skips_pullback_zone() -> None:
    fixture = load_fixture()
    fixture["tickers"]["NVDA"]["range_20d"]["timestamp"] = (
        "2026-06-24T03:00:00-04:00"
    )

    report = generate_daily_market_brief(["NVDA"], AS_OF, fixture)

    assert "Pullback zone not evaluated: 20-day range evidence is stale." in report


def test_pullback_zone_uses_recent_low_when_support_level_is_stale() -> None:
    fixture = load_fixture()
    fixture["tickers"]["NVDA"]["support_level"]["timestamp"] = (
        "2026-06-24T03:00:00-04:00"
    )

    report = generate_daily_market_brief(["NVDA"], AS_OF, fixture)

    assert "Candidate zone for NVDA: 165.00 to 169.95." in report
    assert "Reference price source: range_20d.recent_low_20d" in report


@pytest.mark.parametrize(
    ("mutator", "expected_message"),
    [
        (
            lambda data: data.pop("market_context"),
            "market_context is required",
        ),
        (
            lambda data: data["tickers"]["NVDA"]["quote"].__setitem__(
                "timestamp",
                "2026-06-26 16:00:00",
            ),
            "tickers.NVDA.quote.timestamp must include a timezone offset",
        ),
        (
            lambda data: data["tickers"]["NVDA"]["range_20d"].__setitem__(
                "timestamp",
                "not-a-date",
            ),
            "tickers.NVDA.range_20d.timestamp must be a valid ISO-8601 datetime",
        ),
        (
            lambda data: data["tickers"]["NVDA"]["news"][0].__setitem__(
                "timestamp",
                "2026-06-26T10:00:00",
            ),
            "tickers.NVDA.news[0].timestamp must include a timezone offset",
        ),
        (
            lambda data: data["tickers"]["NVDA"]["quote"].__setitem__(
                "current_price",
                "171.82",
            ),
            "tickers.NVDA.quote.current_price must be a number",
        ),
        (
            lambda data: data["tickers"]["NVDA"]["range_20d"].__setitem__(
                "recent_low_20d",
                None,
            ),
            "tickers.NVDA.range_20d.recent_low_20d must be a number",
        ),
        (
            lambda data: data["tickers"]["NVDA"]["support_level"].__setitem__(
                "price",
                True,
            ),
            "tickers.NVDA.support_level.price must be a number",
        ),
        (
            lambda data: data["market_context"]["indices"][0].__setitem__(
                "change_percent",
                "0.4",
            ),
            "market_context.indices[0].change_percent must be a number",
        ),
        (
            lambda data: data["market_context"]["notes"][0].pop("source"),
            "market_context.notes[0].source is required",
        ),
    ],
)
def test_malformed_fixture_validation_errors(mutator, expected_message: str) -> None:
    fixture = load_fixture()
    mutator(fixture)

    with pytest.raises(ValueError) as exc_info:
        generate_daily_market_brief(["NVDA"], AS_OF, fixture)
    assert str(exc_info.value) == expected_message


def test_as_of_mismatch_raises_validation_error() -> None:
    with pytest.raises(
        ValueError,
        match="fixture.as_of must match invocation as_of exactly",
    ):
        generate_daily_market_brief(
            ["NVDA"],
            "2026-06-27T16:30:00-04:00",
            load_fixture(),
        )


def test_as_of_without_timezone_raises_validation_error() -> None:
    fixture = load_fixture()
    fixture["as_of"] = "2026-06-26T16:30:00"

    with pytest.raises(ValueError, match="as_of must include a timezone offset"):
        generate_daily_market_brief(["NVDA"], "2026-06-26T16:30:00", fixture)


@pytest.mark.parametrize(
    ("mutator", "expected_text"),
    [
        (
            lambda data: data["tickers"]["NVDA"]["range_20d"].__setitem__(
                "timestamp",
                "2026-06-26T16:45:00-04:00",
            ),
            "Pullback zone not evaluated: 20-day range evidence is invalid_future.",
        ),
        (
            lambda data: data["tickers"]["NVDA"]["news"][0].__setitem__(
                "timestamp",
                "2026-06-26T16:45:00-04:00",
            ),
            "freshness invalid_future",
        ),
    ],
)
def test_future_timestamps_are_visible_and_not_fresh(mutator, expected_text) -> None:
    fixture = load_fixture()
    mutator(fixture)

    report = generate_daily_market_brief(["NVDA"], AS_OF, fixture)

    assert expected_text in report


def test_report_avoids_prohibited_finance_advice_wording() -> None:
    report = generate_daily_market_brief(["NVDA"], AS_OF, load_fixture()).lower()

    for phrase in [
        "buy zone",
        "target price",
        "upside",
        "should buy",
        "buy now",
        "place an order",
        "execute",
        "position sizing",
        "guarantees",
    ]:
        assert phrase not in report
    assert "research-only pullback zone" in report
    assert "not personalized financial advice" in report


def test_fixture_backed_output_is_deterministic() -> None:
    fixture = load_fixture()
    clone = copy.deepcopy(fixture)

    first = generate_daily_market_brief(["NVDA", "MSFT"], AS_OF, fixture)
    second = generate_daily_market_brief(["NVDA", "MSFT"], AS_OF, clone)

    assert first == second
