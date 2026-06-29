from __future__ import annotations

import copy
import json
from pathlib import Path

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from hermes_finance import generate_daily_market_brief, generate_entry_zone_strategy
from hermes_runtime.app import app

BASE_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "finance"
    / "base_fixture.json"
)
STRATEGY_FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "finance"
    / "strategy_fixture.json"
)
AS_OF = "2026-06-26T16:30:00-04:00"


def load_base_fixture() -> dict:
    return json.loads(BASE_FIXTURE_PATH.read_text())


def load_strategy_fixture() -> dict:
    return json.loads(STRATEGY_FIXTURE_PATH.read_text())


def build_client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_health_and_ready_are_local_and_route_based() -> None:
    client = build_client()

    registered_routes = {
        (route.path, method)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    }

    health_response = client.get("/health")
    ready_response = client.get("/ready")

    assert ("/finance/daily-market-brief", "POST") in registered_routes
    assert ("/finance/entry-zone-strategy", "POST") in registered_routes
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}
    assert ready_response.status_code == 200
    assert ready_response.json() == {"status": "ready"}


def test_daily_market_brief_returns_exact_finance_markdown() -> None:
    fixture = load_base_fixture()
    payload = {
        "watchlist": ["NVDA", "MSFT"],
        "as_of": AS_OF,
        "fixture": fixture,
    }
    expected = generate_daily_market_brief(
        payload["watchlist"], payload["as_of"], copy.deepcopy(fixture)
    )

    response = build_client().post("/finance/daily-market-brief", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "workflow": "daily_market_brief",
        "as_of": AS_OF,
        "report_markdown": expected,
    }


def test_entry_zone_strategy_returns_exact_finance_markdown() -> None:
    fixture = load_strategy_fixture()
    payload = {
        "watchlist": ["META"],
        "as_of": AS_OF,
        "fixture": fixture,
    }
    expected = generate_entry_zone_strategy(
        payload["watchlist"], payload["as_of"], copy.deepcopy(fixture)
    )

    response = build_client().post("/finance/entry-zone-strategy", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "workflow": "entry_zone_strategy",
        "as_of": AS_OF,
        "report_markdown": expected,
    }


def test_daily_market_brief_passes_request_fields_directly(monkeypatch) -> None:
    calls = []

    def fake_generate(watchlist: list[str], as_of: str, fixture: dict) -> str:
        calls.append((watchlist, as_of, fixture))
        return "daily report"

    monkeypatch.setattr(
        "hermes_runtime.app.generate_daily_market_brief", fake_generate
    )
    fixture = {"as_of": AS_OF, "tickers": {"NVDA": {"quote": {"price": 1}}}}
    payload = {"watchlist": ["NVDA"], "as_of": AS_OF, "fixture": fixture}

    response = build_client().post("/finance/daily-market-brief", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "workflow": "daily_market_brief",
        "as_of": AS_OF,
        "report_markdown": "daily report",
    }
    assert calls == [(["NVDA"], AS_OF, fixture)]


def test_entry_zone_strategy_passes_request_fields_directly(monkeypatch) -> None:
    calls = []

    def fake_generate(watchlist: list[str], as_of: str, fixture: dict) -> str:
        calls.append((watchlist, as_of, fixture))
        return "strategy report"

    monkeypatch.setattr(
        "hermes_runtime.app.generate_entry_zone_strategy", fake_generate
    )
    fixture = {"as_of": AS_OF, "tickers": {"META": {"quote": {"price": 1}}}}
    payload = {"watchlist": ["META"], "as_of": AS_OF, "fixture": fixture}

    response = build_client().post("/finance/entry-zone-strategy", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "workflow": "entry_zone_strategy",
        "as_of": AS_OF,
        "report_markdown": "strategy report",
    }
    assert calls == [(["META"], AS_OF, fixture)]


def test_request_validation_errors_use_normalized_envelope() -> None:
    response = build_client().post(
        "/finance/daily-market-brief",
        json={
            "watchlist": ["NVDA"],
            "as_of": AS_OF,
            "fixture": load_base_fixture(),
            "unexpected": True,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "type": "request_validation",
            "message": "Extra inputs are not permitted",
            "field": "unexpected",
        }
    }


def test_malformed_json_and_non_object_bodies_are_request_validation_errors() -> None:
    malformed_response = build_client().post(
        "/finance/daily-market-brief",
        content='{"watchlist": ["NVDA"',
        headers={"content-type": "application/json"},
    )
    non_object_response = build_client().post(
        "/finance/daily-market-brief",
        json=["NVDA"],
    )

    assert malformed_response.status_code == 422
    assert malformed_response.json()["error"]["type"] == "request_validation"
    assert "detail" not in malformed_response.json()
    assert non_object_response.status_code == 422
    assert non_object_response.json()["error"]["type"] == "request_validation"
    assert "detail" not in non_object_response.json()


def test_wrong_field_types_are_request_validation_errors() -> None:
    response = build_client().post(
        "/finance/daily-market-brief",
        json={"watchlist": "NVDA", "as_of": AS_OF, "fixture": load_base_fixture()},
    )

    assert response.status_code == 422
    assert response.json()["error"]["type"] == "request_validation"
    assert response.json()["error"]["field"] == "watchlist"
    assert "detail" not in response.json()


def test_nested_field_errors_include_top_level_request_field() -> None:
    response = build_client().post(
        "/finance/daily-market-brief",
        json={"watchlist": [1], "as_of": AS_OF, "fixture": load_base_fixture()},
    )

    assert response.status_code == 422
    assert response.json()["error"]["type"] == "request_validation"
    assert response.json()["error"]["field"] == "watchlist"
    assert "detail" not in response.json()


def test_empty_watchlist_is_domain_validation_at_http_boundary() -> None:
    response = build_client().post(
        "/finance/daily-market-brief",
        json={"watchlist": [], "as_of": AS_OF, "fixture": load_base_fixture()},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "type": "domain_validation",
            "message": "Watchlist is empty.",
            "field": "watchlist",
        }
    }


def test_finance_value_error_maps_to_domain_validation() -> None:
    fixture = load_strategy_fixture()
    fixture["tickers"]["META"]["quote"]["timestamp"] = "2026-06-26 16:00:00"

    response = build_client().post(
        "/finance/entry-zone-strategy",
        json={"watchlist": ["META"], "as_of": AS_OF, "fixture": fixture},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "type": "domain_validation",
            "message": (
                "tickers.META.quote.timestamp must include a timezone offset"
            ),
        }
    }


def test_not_found_and_method_not_allowed_use_normalized_envelopes() -> None:
    client = build_client()

    not_found_response = client.get("/finance/unknown")
    docs_response = client.get("/docs")
    method_response = client.get("/finance/daily-market-brief")

    assert not_found_response.status_code == 404
    assert not_found_response.json() == {
        "error": {"type": "not_found", "message": "Route not found."}
    }
    assert docs_response.status_code == 404
    assert docs_response.json() == {
        "error": {"type": "not_found", "message": "Route not found."}
    }
    assert method_response.status_code == 405
    assert method_response.json() == {
        "error": {
            "type": "method_not_allowed",
            "message": "Method not allowed.",
        }
    }


def test_unexpected_internal_errors_are_sanitized(monkeypatch) -> None:
    def boom(watchlist: list[str], as_of: str, fixture: dict) -> str:
        del watchlist
        del as_of
        del fixture
        raise TypeError("leak me")

    monkeypatch.setattr("hermes_runtime.app.generate_daily_market_brief", boom)

    response = build_client().post(
        "/finance/daily-market-brief",
        json={
            "watchlist": ["NVDA"],
            "as_of": AS_OF,
            "fixture": load_base_fixture(),
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "type": "internal_error",
            "message": "Internal runtime error.",
        }
    }
