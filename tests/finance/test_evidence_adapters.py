from __future__ import annotations

import copy
import json
from pathlib import Path

from hermes_finance import generate_daily_market_brief, generate_entry_zone_strategy
from hermes_finance.evidence_adapters import (
    map_daily_market_brief_evidence,
    map_entry_zone_strategy_evidence,
)

AS_OF = "2026-06-26T16:30:00-04:00"
FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "finance"
BRIEF_PAYLOADS_PATH = FIXTURES_DIR / "recorded_brief_payloads.json"
STRATEGY_PAYLOADS_PATH = FIXTURES_DIR / "recorded_strategy_payloads.json"


def load_brief_payloads() -> dict:
    return json.loads(BRIEF_PAYLOADS_PATH.read_text())


def load_strategy_payloads() -> dict:
    return json.loads(STRATEGY_PAYLOADS_PATH.read_text())


def test_daily_market_brief_adapter_maps_complete_fixture_and_renders_report() -> None:
    result = map_daily_market_brief_evidence(
        [" nvda "],
        AS_OF,
        "demo-provider",
        load_brief_payloads(),
    )

    assert result.status == "complete"
    assert result.provider == "demo-provider"
    assert result.as_of == AS_OF
    assert result.diagnostics == []
    assert result.fixture == {
        "as_of": AS_OF,
        "market_context": {
            "indices": [
                {
                    "symbol": "QQQ",
                    "name": "Nasdaq proxy",
                    "price": 580.0,
                    "change_percent": 0.7,
                    "timestamp": "2026-06-26T16:00:00-04:00",
                    "source": "recorded:demo-provider",
                },
                {
                    "symbol": "SPY",
                    "name": "S&P 500 proxy",
                    "price": 650.0,
                    "change_percent": 0.4,
                    "timestamp": "2026-06-26T16:00:00-04:00",
                    "source": "recorded:demo-provider",
                },
            ],
            "notes": [
                {
                    "headline": "Market breadth improved into the close",
                    "timestamp": "2026-06-26T15:45:00-04:00",
                    "source": "recorded:demo-provider",
                }
            ],
        },
        "tickers": {
            "NVDA": {
                "company_name": "NVIDIA Corporation",
                "quote": {
                    "current_price": 171.82,
                    "timestamp": "2026-06-26T16:00:00-04:00",
                    "source": "recorded:demo-provider",
                },
                "range_20d": {
                    "recent_low_20d": 165.0,
                    "recent_high_20d": 184.5,
                    "timestamp": "2026-06-26T16:00:00-04:00",
                    "source": "recorded:demo-provider",
                },
                "support_level": {
                    "price": 166.0,
                    "timestamp": "2026-06-26T16:00:00-04:00",
                    "source": "recorded:demo-provider",
                },
                "news": [
                    {
                        "headline": "Example headline",
                        "summary": "Short fixture-backed summary.",
                        "timestamp": "2026-06-26T10:00:00-04:00",
                        "source": "recorded:demo-provider",
                    }
                ],
            }
        },
    }

    report = generate_daily_market_brief(["NVDA"], AS_OF, result.fixture)
    assert "## NVDA - NVIDIA Corporation" in report
    assert "Candidate zone for NVDA: 166.00 to 170.98." in report


def test_entry_zone_strategy_adapter_maps_complete_fixture_and_renders_report() -> None:
    result = map_entry_zone_strategy_evidence(
        [" meta "],
        AS_OF,
        "demo-provider",
        load_strategy_payloads(),
    )

    assert result.status == "complete"
    assert result.provider == "demo-provider"
    assert result.as_of == AS_OF
    assert result.diagnostics == []
    assert result.fixture == {
        "as_of": AS_OF,
        "tickers": {
            "META": {
                "company_name": "Meta Platforms, Inc.",
                "quote": {
                    "current_price": 682.35,
                    "timestamp": "2026-06-26T16:00:00-04:00",
                    "source": "recorded:demo-provider",
                },
                "strategy": {
                    "moving_averages": {
                        "sma_50": 660.0,
                        "sma_200": 575.0,
                        "timestamp": "2026-06-26T16:00:00-04:00",
                        "source": "recorded:demo-provider",
                    },
                    "momentum": {
                        "rsi_14": 54.2,
                        "timestamp": "2026-06-26T16:00:00-04:00",
                        "source": "recorded:demo-provider",
                    },
                    "range_52w": {
                        "low": 442.65,
                        "high": 740.91,
                        "timestamp": "2026-06-26T16:00:00-04:00",
                        "source": "recorded:demo-provider",
                    },
                    "support_resistance": {
                        "support_1": 650.0,
                        "resistance_1": 720.0,
                        "timestamp": "2026-06-26T16:00:00-04:00",
                        "source": "recorded:demo-provider",
                    },
                    "volatility": {
                        "atr_14": 18.25,
                        "timestamp": "2026-06-26T16:00:00-04:00",
                        "source": "recorded:demo-provider",
                    },
                    "volume": {
                        "latest_volume": 14500000,
                        "avg_volume_20d": 13200000,
                        "timestamp": "2026-06-26T16:00:00-04:00",
                        "source": "recorded:demo-provider",
                    },
                },
            }
        },
    }

    report = generate_entry_zone_strategy(["META"], AS_OF, result.fixture)
    assert "Technical setup score for META: 98/100." in report
    assert (
        "| 1 | META | High-scoring research candidate | 98 | "
        "650.00 to 677.38 |" in report
    )


def test_adapter_keeps_keyed_symbol_ownership_without_inner_symbol_fields() -> None:
    brief_payloads = load_brief_payloads()
    del brief_payloads["market_context"]["SPY"]["symbol"]
    del brief_payloads["market_context"]["QQQ"]["symbol"]
    del brief_payloads["quotes"]["NVDA"]["symbol"]
    del brief_payloads["ranges"]["NVDA"]["symbol"]
    del brief_payloads["support_levels"]["NVDA"]["symbol"]

    brief_result = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        brief_payloads,
    )

    assert brief_result.status == "complete"
    assert brief_result.diagnostics == []
    assert brief_result.fixture["market_context"]["indices"][0]["symbol"] == "QQQ"
    assert brief_result.fixture["market_context"]["indices"][1]["symbol"] == "SPY"

    strategy_payloads = load_strategy_payloads()
    del strategy_payloads["quotes"]["META"]["symbol"]
    del strategy_payloads["moving_averages"]["META"]["symbol"]
    del strategy_payloads["momentum"]["META"]["symbol"]
    del strategy_payloads["range_52w"]["META"]["symbol"]
    del strategy_payloads["support_resistance"]["META"]["symbol"]
    del strategy_payloads["volatility"]["META"]["symbol"]
    del strategy_payloads["volume"]["META"]["symbol"]

    strategy_result = map_entry_zone_strategy_evidence(
        ["META"],
        AS_OF,
        "demo-provider",
        strategy_payloads,
    )

    assert strategy_result.status == "complete"
    assert strategy_result.diagnostics == []


def test_adapter_canonicalizes_recorded_provider_provenance() -> None:
    payloads = load_brief_payloads()
    payloads["quotes"]["NVDA"]["source"] = "live-websocket"
    payloads["ranges"]["NVDA"]["source"] = "provider-rest"
    payloads["support_levels"]["NVDA"]["source"] = "snapshot-feed"
    payloads["news"]["NVDA"][0]["source"] = "breaking-news-wire"

    result = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "complete"
    assert result.fixture["tickers"]["NVDA"]["quote"]["source"] == (
        "recorded:demo-provider"
    )
    assert result.fixture["tickers"]["NVDA"]["range_20d"]["source"] == (
        "recorded:demo-provider"
    )
    assert result.fixture["tickers"]["NVDA"]["support_level"]["source"] == (
        "recorded:demo-provider"
    )
    assert result.fixture["tickers"]["NVDA"]["news"][0]["source"] == (
        "recorded:demo-provider"
    )


def test_brief_adapter_orders_diagnostics_deterministically_for_partial_payloads(
) -> None:
    payloads = load_brief_payloads()
    payloads["moving_averages"] = {
        "NVDA": {
            "symbol": "NVDA",
            "sma_50": 168.0,
            "sma_200": 150.0,
            "timestamp": "2026-06-26T16:00:00-04:00",
            "source": "recorded:demo-provider",
        }
    }
    payloads["unknown_blob"] = {"foo": "bar"}
    del payloads["ranges"]["NVDA"]
    del payloads["news"]["NVDA"]

    result = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert result.fixture is not None
    assert [diag.type for diag in result.diagnostics] == [
        "skipped_evidence_group",
        "unknown_evidence_group",
        "partial_payload",
        "partial_payload",
    ]
    assert [diag.field for diag in result.diagnostics] == [
        "moving_averages",
        "unknown_blob",
        "ranges",
        "news",
    ]
    report = generate_daily_market_brief(["NVDA"], AS_OF, result.fixture)
    assert "20-day range: unavailable." in report
    assert "News: unavailable." in report


def test_brief_adapter_drops_bad_market_context_timestamps_without_failing() -> None:
    payloads = load_brief_payloads()
    del payloads["market_context"]["SPY"]["timestamp"]
    payloads["market_context"]["notes"][0]["timestamp"] = "not-a-date"

    result = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert result.fixture is not None
    assert [diag.type for diag in result.diagnostics] == [
        "missing_field",
        "invalid_timestamp",
    ]
    assert result.fixture["market_context"]["indices"] == [
        {
            "symbol": "QQQ",
            "name": "Nasdaq proxy",
            "price": 580.0,
            "change_percent": 0.7,
            "timestamp": "2026-06-26T16:00:00-04:00",
            "source": "recorded:demo-provider",
        }
    ]
    assert result.fixture["market_context"]["notes"] == []

    report = generate_daily_market_brief(["NVDA"], AS_OF, result.fixture)
    assert "Context completeness: incomplete" in report
    assert "Market note:" not in report


def test_brief_adapter_reports_stale_and_future_timestamps_without_dropping_fixture(
) -> None:
    payloads = load_brief_payloads()
    payloads["quotes"]["NVDA"]["timestamp"] = "2026-06-24T03:00:00-04:00"
    payloads["support_levels"]["NVDA"]["timestamp"] = "2026-06-26T16:45:00-04:00"

    result = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert [diag.type for diag in result.diagnostics] == [
        "stale_timestamp",
        "future_timestamp",
    ]
    report = generate_daily_market_brief(["NVDA"], AS_OF, result.fixture)
    assert "Pullback zone not evaluated: quote evidence is stale." in report
    assert "freshness invalid_future" in report


def test_strategy_adapter_reports_stale_and_future_timestamps_without_dropping_fixture(
) -> None:
    payloads = load_strategy_payloads()
    payloads["moving_averages"]["META"]["timestamp"] = "2026-06-18T16:00:00-04:00"
    payloads["support_resistance"]["META"]["timestamp"] = "2026-06-26T16:45:00-04:00"

    result = map_entry_zone_strategy_evidence(
        ["META"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert [diag.type for diag in result.diagnostics] == [
        "stale_timestamp",
        "future_timestamp",
    ]
    report = generate_entry_zone_strategy(["META"], AS_OF, result.fixture)
    assert "strategy.moving_averages evidence is stale" in report
    assert "strategy.support_resistance evidence is invalid_future" in report


def test_brief_adapter_maps_invalid_and_unsupported_symbols_into_invalid_inputs(
) -> None:
    payloads = load_brief_payloads()
    payloads["quotes"] = {
        "BRK.B": {
            "status": "invalid_symbol",
            "message": "Ambiguous class/share formatting in recording",
        },
        "XYZ": {
            "status": "unsupported_symbol",
            "message": "Provider does not support XYZ",
        },
    }
    payloads["ranges"] = {}
    payloads["support_levels"] = {}
    payloads["news"] = {}

    result = map_daily_market_brief_evidence(
        ["BRK.B", "XYZ"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert result.fixture is not None
    assert result.fixture["invalid_inputs"] == {
        "BRK.B": "Ambiguous class/share formatting in recording",
        "XYZ": "Provider does not support XYZ",
    }
    assert [diag.type for diag in result.diagnostics[:2]] == [
        "invalid_symbol",
        "unsupported_symbol",
    ]


def test_strategy_adapter_reports_provider_error_and_missing_provenance() -> None:
    payloads = load_strategy_payloads()
    payloads["volatility"]["META"] = {
        "status": "error",
        "message": "Recorded provider timeout",
    }
    del payloads["volume"]["META"]["source"]

    result = map_entry_zone_strategy_evidence(
        ["META"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert [diag.type for diag in result.diagnostics] == [
        "provider_error",
        "missing_provenance",
    ]
    report = generate_entry_zone_strategy(["META"], AS_OF, result.fixture)
    assert "strategy.volatility evidence is unavailable" in report
    assert "strategy.volume evidence is unavailable" in report


def test_brief_adapter_reports_symbol_mismatch() -> None:
    payloads = load_brief_payloads()
    payloads["quotes"]["NVDA"]["symbol"] = "AMD"

    result = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert [diag.type for diag in result.diagnostics] == ["symbol_mismatch"]
    assert result.diagnostics[0].symbol == "NVDA"
    assert result.fixture is not None
    report = generate_daily_market_brief(["NVDA"], AS_OF, result.fixture)
    assert "- Quote: unavailable." in report


def test_strategy_adapter_reports_malformed_symbol_group_payload() -> None:
    payloads = load_strategy_payloads()
    payloads["momentum"]["META"] = 42

    result = map_entry_zone_strategy_evidence(
        ["META"],
        AS_OF,
        "demo-provider",
        payloads,
    )

    assert result.status == "partial"
    assert [diag.type for diag in result.diagnostics] == ["malformed_payload"]
    assert result.diagnostics[0].field == "momentum"
    report = generate_entry_zone_strategy(["META"], AS_OF, result.fixture)
    assert "strategy.momentum evidence is unavailable" in report


def test_adapter_does_not_mutate_input_payloads() -> None:
    brief_payloads = load_brief_payloads()
    brief_original = copy.deepcopy(brief_payloads)
    strategy_payloads = load_strategy_payloads()
    strategy_original = copy.deepcopy(strategy_payloads)

    _ = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        brief_payloads,
    )
    _ = map_entry_zone_strategy_evidence(
        ["META"],
        AS_OF,
        "demo-provider",
        strategy_payloads,
    )

    assert brief_payloads == brief_original
    assert strategy_payloads == strategy_original


def test_adapter_returns_failed_result_for_malformed_top_level_payloads() -> None:
    result = map_daily_market_brief_evidence(
        ["NVDA"],
        AS_OF,
        "demo-provider",
        copy.deepcopy(["not", "a", "mapping"]),  # type: ignore[arg-type]
    )

    assert result.status == "failed"
    assert result.fixture is None
    assert [diag.type for diag in result.diagnostics] == ["malformed_payload"]
