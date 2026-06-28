from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from hermes_finance._brief_utils import (
    ensure_mapping,
    get_required_list,
    get_required_mapping,
    get_required_number,
    get_required_string,
    has_required_market_proxies,
    is_list_like,
    normalize_ticker,
    parse_iso_datetime,
)


@dataclass(frozen=True)
class EvidenceSnapshot:
    as_of: str
    as_of_dt: datetime
    invalid_inputs: Mapping[str, str]
    market_context: Mapping[str, Sequence[object]]
    market_context_complete: bool
    tickers: Mapping[str, Mapping[str, object]]


class EvidenceSnapshotValidator:
    def validate(self, fixture: dict, as_of: str) -> EvidenceSnapshot:
        if not isinstance(fixture, Mapping):
            raise ValueError("fixture must be a mapping")

        fixture_as_of = fixture.get("as_of")
        if fixture_as_of != as_of:
            raise ValueError("fixture.as_of must match invocation as_of exactly")
        as_of_dt = parse_iso_datetime(as_of, "as_of")

        market_context = get_required_mapping(fixture, "market_context")
        indices = get_required_list(
            market_context, "indices", "market_context.indices"
        )
        notes = market_context.get("notes", [])
        if not is_list_like(notes):
            raise ValueError("market_context.notes must be a list when present")

        tickers = get_required_mapping(fixture, "tickers")
        invalid_inputs = fixture.get("invalid_inputs", {})
        if not isinstance(invalid_inputs, Mapping):
            raise ValueError("invalid_inputs must be an object when present")

        normalized_invalid_inputs: dict[str, str] = {}
        for symbol, reason in invalid_inputs.items():
            if not isinstance(symbol, str) or not isinstance(reason, str):
                raise ValueError("invalid_inputs keys and values must be strings")
            normalized_invalid_inputs[normalize_ticker(symbol)] = reason

        normalized_tickers: dict[str, Mapping[str, object]] = {}
        for symbol, payload in tickers.items():
            if not isinstance(symbol, str):
                raise ValueError("tickers keys must be strings")
            if not isinstance(payload, Mapping):
                raise ValueError(f"tickers.{symbol} must be an object")
            normalized = normalize_ticker(symbol)
            if normalized in normalized_invalid_inputs:
                raise ValueError(
                    f"ticker {normalized} cannot appear in both tickers and "
                    "invalid_inputs"
                )
            normalized_tickers[normalized] = payload

        self._validate_market_indices(indices)
        self._validate_market_notes(notes)
        for symbol, payload in normalized_tickers.items():
            self._validate_ticker_shape(symbol, payload)

        return EvidenceSnapshot(
            as_of=fixture_as_of,
            as_of_dt=as_of_dt,
            invalid_inputs=normalized_invalid_inputs,
            market_context={"indices": list(indices), "notes": list(notes)},
            market_context_complete=has_required_market_proxies(indices),
            tickers=normalized_tickers,
        )

    def _validate_market_indices(self, indices: Sequence[object]) -> None:
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
            get_required_number(entry, "price", f"{path}.price")
            get_required_number(entry, "change_percent", f"{path}.change_percent")
            parse_iso_datetime(
                get_required_string(entry, "timestamp", f"{path}.timestamp"),
                f"{path}.timestamp",
            )

    def _validate_market_notes(self, notes: Sequence[object]) -> None:
        for index, note in enumerate(notes):
            path = f"market_context.notes[{index}]"
            if not isinstance(note, Mapping):
                raise ValueError(f"{path} must be an object")
            for field in ("headline", "timestamp", "source"):
                if field not in note:
                    raise ValueError(f"{path}.{field} is required")
            parse_iso_datetime(
                get_required_string(note, "timestamp", f"{path}.timestamp"),
                f"{path}.timestamp",
            )

    def _validate_ticker_shape(
        self, symbol: str, payload: Mapping[str, object]
    ) -> None:
        quote = payload.get("quote")
        if quote is not None:
            quote_mapping = ensure_mapping(quote, f"tickers.{symbol}.quote")
            if "current_price" not in quote_mapping:
                raise ValueError(
                    f"tickers.{symbol}.quote.current_price is required when "
                    "quote exists"
                )
            if "source" not in quote_mapping:
                raise ValueError(
                    f"tickers.{symbol}.quote.source is required when quote exists"
                )
            get_required_number(
                quote_mapping,
                "current_price",
                f"tickers.{symbol}.quote.current_price",
            )
            timestamp = quote_mapping.get("timestamp")
            if timestamp is not None:
                parse_iso_datetime(
                    get_required_string(
                        quote_mapping,
                        "timestamp",
                        f"tickers.{symbol}.quote.timestamp",
                    ),
                    f"tickers.{symbol}.quote.timestamp",
                )

        range_data = payload.get("range_20d")
        if range_data is not None:
            range_mapping = ensure_mapping(range_data, f"tickers.{symbol}.range_20d")
            for field in ("recent_low_20d", "recent_high_20d", "source"):
                if field not in range_mapping:
                    raise ValueError(
                        f"tickers.{symbol}.range_20d.{field} is required "
                        "when range_20d exists"
                    )
            get_required_number(
                range_mapping,
                "recent_low_20d",
                f"tickers.{symbol}.range_20d.recent_low_20d",
            )
            get_required_number(
                range_mapping,
                "recent_high_20d",
                f"tickers.{symbol}.range_20d.recent_high_20d",
            )
            timestamp = range_mapping.get("timestamp")
            if timestamp is not None:
                parse_iso_datetime(
                    get_required_string(
                        range_mapping,
                        "timestamp",
                        f"tickers.{symbol}.range_20d.timestamp",
                    ),
                    f"tickers.{symbol}.range_20d.timestamp",
                )

        support_level = payload.get("support_level")
        if support_level is not None:
            support_mapping = ensure_mapping(
                support_level,
                f"tickers.{symbol}.support_level",
            )
            if "price" not in support_mapping:
                raise ValueError(
                    f"tickers.{symbol}.support_level.price is required "
                    "when support_level exists"
                )
            get_required_number(
                support_mapping,
                "price",
                f"tickers.{symbol}.support_level.price",
            )
            timestamp = support_mapping.get("timestamp")
            if timestamp is not None:
                parse_iso_datetime(
                    get_required_string(
                        support_mapping,
                        "timestamp",
                        f"tickers.{symbol}.support_level.timestamp",
                    ),
                    f"tickers.{symbol}.support_level.timestamp",
                )

        news = payload.get("news", [])
        if news is None:
            return
        if not is_list_like(news):
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
                parse_iso_datetime(
                    get_required_string(item, "timestamp", f"{path}.timestamp"),
                    f"{path}.timestamp",
                )
