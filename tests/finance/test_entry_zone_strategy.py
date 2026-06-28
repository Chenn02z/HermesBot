from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from hermes_finance import generate_entry_zone_strategy
from hermes_finance.entry_zone_strategy import (
    generate_entry_zone_strategy as public_generate_entry_zone_strategy,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "finance"
    / "strategy_fixture.json"
)
AS_OF = "2026-06-26T16:30:00-04:00"
REQUIRED_STRATEGY_GROUPS = (
    "moving_averages",
    "momentum",
    "range_52w",
    "support_resistance",
    "volatility",
    "volume",
)


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text())


def test_public_api_is_exposed_from_package_and_module() -> None:
    assert public_generate_entry_zone_strategy is generate_entry_zone_strategy


def test_valid_meta_report_renders_deterministic_score_and_observation_zone() -> None:
    report = generate_entry_zone_strategy(["META"], AS_OF, load_fixture())

    assert report.startswith(f"# Entry-Zone Strategy ({AS_OF})")
    assert "## Method Summary" in report
    assert "## Watchlist Coverage Summary" in report
    assert (
        "| 1 | META | High-scoring research candidate | 98 | 650.00 to 677.38 |"
        in report
    )
    assert "## META - Meta Platforms, Inc." in report
    assert "Technical setup score for META: 98/100." in report
    assert "- Trend quality: 25/25." in report
    assert "- Pullback and location quality: 23/25." in report
    assert "- Momentum quality: 20/20." in report
    assert "- Volume quality: 15/15." in report
    assert "- Volatility quality: 15/15." in report
    assert "- Research-candidate label: High-scoring research candidate." in report
    assert "- Observation zone: 650.00 to 677.38." in report
    assert "### Conflict Notes\n- none" in report
    assert "## Limitations" in report


def test_comparison_table_sorts_scores_then_ties_then_unscored() -> None:
    report = generate_entry_zone_strategy(
        ["AMZN", "MSFT", "NVDA", "META"],
        AS_OF,
        load_fixture(),
    )

    meta_row = "| 1 | META | High-scoring research candidate | 98 | 650.00 to 677.38 |"
    msft_row = "| 2 | MSFT | High-scoring research candidate | 76 | 470.00 to 493.50 |"
    nvda_row = "| 3 | NVDA | High-scoring research candidate | 76 | 160.00 to 168.00 |"
    amzn_row = "| - | AMZN | Insufficient fresh evidence | not scored | not evaluated |"
    assert (
        report.index(meta_row)
        < report.index(msft_row)
        < report.index(nvda_row)
        < report.index(amzn_row)
    )


def test_empty_duplicate_unsupported_and_ambiguous_inputs_render_visibly() -> None:
    empty = generate_entry_zone_strategy([], AS_OF, load_fixture())
    assert "## Validation Failure" in empty
    assert "Watchlist is empty." in empty

    report = generate_entry_zone_strategy(
        [" meta ", "BRK.B", "MSFT", "META", "XYZ"],
        AS_OF,
        load_fixture(),
    )
    assert "Supported unique normalized tickers: META, MSFT." in report
    assert (
        "Duplicate normalized tickers skipped after first occurrence: META." in report
    )
    assert (
        "Ambiguous inputs: BRK.B (Ambiguous class/share formatting in fixture)."
        in report
    )
    assert "Unsupported inputs: XYZ." in report
    assert "## Ambiguous Input - BRK.B" in report
    assert "## Unsupported Input - XYZ" in report


def test_missing_stale_future_and_missing_groups_degrade_visibly() -> None:
    fixture = load_fixture()
    del fixture["tickers"]["AMZN"]["strategy"]["volatility"]
    fixture["tickers"]["META"]["strategy"]["volume"]["timestamp"] = (
        "2026-06-18T16:00:00-04:00"
    )
    fixture["tickers"]["MSFT"]["quote"]["timestamp"] = "2026-06-24T03:00:00-04:00"
    fixture["tickers"]["NVDA"]["strategy"]["support_resistance"]["timestamp"] = (
        "2026-06-26T16:45:00-04:00"
    )

    report = generate_entry_zone_strategy(
        ["AMZN", "META", "MSFT", "NVDA"], AS_OF, fixture
    )

    assert "strategy.volatility evidence is unavailable" in report
    assert "strategy.volume evidence is stale" in report
    assert "quote evidence is stale" in report
    assert "strategy.support_resistance evidence is invalid_future" in report
    assert (
        "| - | AMZN | Insufficient fresh evidence | not scored | not evaluated |"
        in report
    )
    assert (
        "| - | META | Insufficient fresh evidence | not scored | not evaluated |"
        in report
    )
    assert (
        "| - | MSFT | Insufficient fresh evidence | not scored | not evaluated |"
        in report
    )
    assert (
        "| - | NVDA | Insufficient fresh evidence | not scored | not evaluated |"
        in report
    )


@pytest.mark.parametrize("group_name", REQUIRED_STRATEGY_GROUPS)
def test_each_missing_required_strategy_group_degrades_visibly(
    group_name: str,
) -> None:
    fixture = load_fixture()
    del fixture["tickers"]["META"]["strategy"][group_name]

    report = generate_entry_zone_strategy(["META"], AS_OF, fixture)

    assert f"strategy.{group_name} evidence is unavailable" in report
    assert (
        "| - | META | Insufficient fresh evidence | not scored | not evaluated |"
        in report
    )


@pytest.mark.parametrize("group_name", REQUIRED_STRATEGY_GROUPS)
def test_missing_strategy_group_timestamp_degrades_as_stale(group_name: str) -> None:
    fixture = load_fixture()
    del fixture["tickers"]["META"]["strategy"][group_name]["timestamp"]

    report = generate_entry_zone_strategy(["META"], AS_OF, fixture)

    assert f"strategy.{group_name} evidence is stale" in report
    assert (
        "| - | META | Insufficient fresh evidence | not scored | not evaluated |"
        in report
    )


@pytest.mark.parametrize(
    ("mutator", "expected_message"),
    [
        (
            lambda data: data.pop("tickers"),
            "tickers is required",
        ),
        (
            lambda data: data["tickers"]["META"]["quote"].__setitem__(
                "timestamp", "2026-06-26 16:00:00"
            ),
            "tickers.META.quote.timestamp must include a timezone offset",
        ),
        (
            lambda data: data["tickers"]["META"]["strategy"]["momentum"].__setitem__(
                "timestamp", "not-a-date"
            ),
            (
                "tickers.META.strategy.momentum.timestamp must be a valid "
                "ISO-8601 datetime"
            ),
        ),
        (
            lambda data: data["tickers"]["META"]["quote"].__setitem__(
                "current_price", 0
            ),
            "tickers.META.quote.current_price must be greater than zero",
        ),
        (
            lambda data: data["tickers"]["META"]["strategy"][
                "moving_averages"
            ].__setitem__("sma_50", True),
            "tickers.META.strategy.moving_averages.sma_50 must be a number",
        ),
        (
            lambda data: data["tickers"]["META"]["strategy"]["momentum"].__setitem__(
                "rsi_14", 101
            ),
            "tickers.META.strategy.momentum.rsi_14 must be between 0 and 100 inclusive",
        ),
        (
            lambda data: data["tickers"]["META"]["strategy"]["range_52w"].__setitem__(
                "low", 800
            ),
            (
                "tickers.META.strategy.range_52w.low must be less than or "
                "equal to tickers.META.strategy.range_52w.high"
            ),
        ),
        (
            lambda data: data["tickers"]["META"]["strategy"][
                "support_resistance"
            ].__setitem__("support_1", 800),
            (
                "tickers.META.strategy.support_resistance.support_1 must be "
                "less than "
                "tickers.META.strategy.support_resistance.resistance_1"
            ),
        ),
        (
            lambda data: data["tickers"]["META"]["strategy"]["volume"].__setitem__(
                "avg_volume_20d", 0
            ),
            "tickers.META.strategy.volume.avg_volume_20d must be greater than zero",
        ),
        (
            lambda data: data["tickers"]["META"]["strategy"]["volatility"].__setitem__(
                "atr_14", 0
            ),
            "tickers.META.strategy.volatility.atr_14 must be greater than zero",
        ),
    ],
)
def test_invalid_values_raise_validation_errors(mutator, expected_message: str) -> None:
    fixture = load_fixture()
    mutator(fixture)

    with pytest.raises(ValueError) as exc_info:
        generate_entry_zone_strategy(["META"], AS_OF, fixture)
    assert str(exc_info.value) == expected_message


def test_as_of_mismatch_and_missing_timezone_raise_validation_errors() -> None:
    with pytest.raises(
        ValueError, match="fixture.as_of must match invocation as_of exactly"
    ):
        generate_entry_zone_strategy(
            ["META"], "2026-06-27T16:30:00-04:00", load_fixture()
        )

    fixture = load_fixture()
    fixture["as_of"] = "2026-06-26T16:30:00"
    with pytest.raises(ValueError, match="as_of must include a timezone offset"):
        generate_entry_zone_strategy(["META"], "2026-06-26T16:30:00", fixture)


def test_conflict_notes_render_without_suppressing_score() -> None:
    report = generate_entry_zone_strategy(["TSLA"], AS_OF, load_fixture())

    assert "| 1 | TSLA | Weak research candidate | 33 | 280.00 to 294.00 |" in report
    assert "50-day moving average is at or below the 200-day moving average." in report
    assert "Current price is below the 200-day moving average." in report
    assert "Current price is below the 50-day moving average." in report
    assert "Resistance is at or below the current price." in report
    assert "RSI sits outside the 30 to 70 range." in report
    assert "Volume ratio is outside the 0.5 to 2.5 range." in report
    assert "ATR ratio is above 0.06." in report


def test_observation_zone_skip_conditions_render_reasons() -> None:
    fixture = load_fixture()
    fixture["tickers"]["META"]["strategy"]["support_resistance"]["timestamp"] = (
        "2026-06-18T16:00:00-04:00"
    )
    report = generate_entry_zone_strategy(["META"], AS_OF, fixture)
    assert (
        "Observation zone not evaluated: strategy.support_resistance evidence is stale."
        in report
    )

    fixture = load_fixture()
    fixture["tickers"]["META"]["strategy"]["volatility"]["timestamp"] = (
        "2026-06-18T16:00:00-04:00"
    )
    report = generate_entry_zone_strategy(["META"], AS_OF, fixture)
    assert (
        "Observation zone not evaluated: strategy.volatility evidence is stale."
        in report
    )

    fixture = load_fixture()
    fixture["tickers"]["META"]["strategy"]["support_resistance"]["support_1"] = 690.0
    report = generate_entry_zone_strategy(["META"], AS_OF, fixture)
    assert (
        "Observation zone not evaluated: support is at or above the current price."
        in report
    )

    fixture = load_fixture()
    fixture["tickers"]["NVDA"]["strategy"]["support_resistance"]["support_1"] = 170.0
    report = generate_entry_zone_strategy(["NVDA"], AS_OF, fixture)
    assert (
        "Observation zone not evaluated: current price is already inside or "
        "below the observation zone." in report
    )


def test_output_is_deterministic_and_avoids_prohibited_wording() -> None:
    fixture = load_fixture()
    clone = copy.deepcopy(fixture)

    first = generate_entry_zone_strategy(["META", "MSFT"], AS_OF, fixture)
    second = generate_entry_zone_strategy(["META", "MSFT"], AS_OF, clone)

    assert first == second

    lower = first.lower()
    for phrase in [
        "buy zone",
        "target price",
        "upside",
        "should buy",
        "buy now",
        "place an order",
        "execute",
        "entry recommendation",
        "recommended entry",
        "accumulate now",
    ]:
        assert phrase not in lower
    assert "entry-zone strategy" in lower
    assert "observation zone" in lower
    assert "not personalized financial advice" in lower
