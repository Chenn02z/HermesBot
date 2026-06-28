from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from hermes_finance._brief_utils import (
    ensure_mapping,
    get_required_mapping,
    get_required_number,
    get_required_string,
    normalize_ticker,
    parse_iso_datetime,
)

REQUIRED_STRATEGY_GROUPS = (
    "moving_averages",
    "momentum",
    "range_52w",
    "support_resistance",
    "volatility",
    "volume",
)


@dataclass(frozen=True)
class StrategySnapshot:
    as_of: str
    as_of_dt: datetime
    invalid_inputs: Mapping[str, str]
    tickers: Mapping[str, Mapping[str, object]]


class StrategySnapshotValidator:
    def validate(self, fixture: dict, as_of: str) -> StrategySnapshot:
        if not isinstance(fixture, Mapping):
            raise ValueError("fixture must be a mapping")

        fixture_as_of = fixture.get("as_of")
        if fixture_as_of != as_of:
            raise ValueError("fixture.as_of must match invocation as_of exactly")
        as_of_dt = parse_iso_datetime(as_of, "as_of")

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
            self._validate_ticker_shape(normalized, payload)
            normalized_tickers[normalized] = payload

        return StrategySnapshot(
            as_of=fixture_as_of,
            as_of_dt=as_of_dt,
            invalid_inputs=normalized_invalid_inputs,
            tickers=normalized_tickers,
        )

    def _validate_ticker_shape(
        self, symbol: str, payload: Mapping[str, object]
    ) -> None:
        company_name = payload.get("company_name")
        if company_name is not None and not isinstance(company_name, str):
            raise ValueError(f"tickers.{symbol}.company_name must be a string")

        quote = payload.get("quote")
        if quote is not None:
            self._validate_quote(
                symbol, ensure_mapping(quote, f"tickers.{symbol}.quote")
            )

        strategy = payload.get("strategy")
        if strategy is not None:
            strategy_mapping = ensure_mapping(strategy, f"tickers.{symbol}.strategy")
            for group in REQUIRED_STRATEGY_GROUPS:
                group_value = strategy_mapping.get(group)
                if group_value is None:
                    continue
                group_mapping = ensure_mapping(
                    group_value,
                    f"tickers.{symbol}.strategy.{group}",
                )
                getattr(self, f"_validate_{group}")(symbol, group_mapping)

    def _validate_quote(self, symbol: str, quote: Mapping[str, object]) -> None:
        path = f"tickers.{symbol}.quote"
        if "current_price" not in quote:
            raise ValueError(f"{path}.current_price is required when quote exists")
        if "source" not in quote:
            raise ValueError(f"{path}.source is required when quote exists")
        current_price = get_required_number(
            quote, "current_price", f"{path}.current_price"
        )
        if current_price <= 0:
            raise ValueError(f"{path}.current_price must be greater than zero")
        get_required_string(quote, "source", f"{path}.source")
        timestamp = quote.get("timestamp")
        if timestamp is not None:
            parse_iso_datetime(
                get_required_string(quote, "timestamp", f"{path}.timestamp"),
                f"{path}.timestamp",
            )

    def _validate_moving_averages(
        self, symbol: str, group: Mapping[str, object]
    ) -> None:
        path = f"tickers.{symbol}.strategy.moving_averages"
        for field in ("sma_50", "sma_200", "source"):
            if field not in group:
                raise ValueError(
                    f"{path}.{field} is required when moving_averages exists"
                )
        for field in ("sma_50", "sma_200"):
            value = get_required_number(group, field, f"{path}.{field}")
            if value <= 0:
                raise ValueError(f"{path}.{field} must be greater than zero")
        self._validate_timestamped_group(path, group)

    def _validate_momentum(self, symbol: str, group: Mapping[str, object]) -> None:
        path = f"tickers.{symbol}.strategy.momentum"
        for field in ("rsi_14", "source"):
            if field not in group:
                raise ValueError(f"{path}.{field} is required when momentum exists")
        rsi = get_required_number(group, "rsi_14", f"{path}.rsi_14")
        if rsi < 0 or rsi > 100:
            raise ValueError(f"{path}.rsi_14 must be between 0 and 100 inclusive")
        self._validate_timestamped_group(path, group)

    def _validate_range_52w(self, symbol: str, group: Mapping[str, object]) -> None:
        path = f"tickers.{symbol}.strategy.range_52w"
        for field in ("low", "high", "source"):
            if field not in group:
                raise ValueError(f"{path}.{field} is required when range_52w exists")
        low = get_required_number(group, "low", f"{path}.low")
        high = get_required_number(group, "high", f"{path}.high")
        if low <= 0:
            raise ValueError(f"{path}.low must be greater than zero")
        if high <= 0:
            raise ValueError(f"{path}.high must be greater than zero")
        if low > high:
            raise ValueError(f"{path}.low must be less than or equal to {path}.high")
        self._validate_timestamped_group(path, group)

    def _validate_support_resistance(
        self, symbol: str, group: Mapping[str, object]
    ) -> None:
        path = f"tickers.{symbol}.strategy.support_resistance"
        for field in ("support_1", "resistance_1", "source"):
            if field not in group:
                raise ValueError(
                    f"{path}.{field} is required when support_resistance exists"
                )
        support = get_required_number(group, "support_1", f"{path}.support_1")
        resistance = get_required_number(group, "resistance_1", f"{path}.resistance_1")
        if support <= 0:
            raise ValueError(f"{path}.support_1 must be greater than zero")
        if resistance <= 0:
            raise ValueError(f"{path}.resistance_1 must be greater than zero")
        if support >= resistance:
            raise ValueError(f"{path}.support_1 must be less than {path}.resistance_1")
        self._validate_timestamped_group(path, group)

    def _validate_volatility(self, symbol: str, group: Mapping[str, object]) -> None:
        path = f"tickers.{symbol}.strategy.volatility"
        for field in ("atr_14", "source"):
            if field not in group:
                raise ValueError(f"{path}.{field} is required when volatility exists")
        atr = get_required_number(group, "atr_14", f"{path}.atr_14")
        if atr <= 0:
            raise ValueError(f"{path}.atr_14 must be greater than zero")
        self._validate_timestamped_group(path, group)

    def _validate_volume(self, symbol: str, group: Mapping[str, object]) -> None:
        path = f"tickers.{symbol}.strategy.volume"
        for field in ("latest_volume", "avg_volume_20d", "source"):
            if field not in group:
                raise ValueError(f"{path}.{field} is required when volume exists")
        latest_volume = get_required_number(
            group, "latest_volume", f"{path}.latest_volume"
        )
        avg_volume = get_required_number(
            group, "avg_volume_20d", f"{path}.avg_volume_20d"
        )
        if latest_volume <= 0:
            raise ValueError(f"{path}.latest_volume must be greater than zero")
        if avg_volume <= 0:
            raise ValueError(f"{path}.avg_volume_20d must be greater than zero")
        self._validate_timestamped_group(path, group)

    def _validate_timestamped_group(
        self, path: str, group: Mapping[str, object]
    ) -> None:
        get_required_string(group, "source", f"{path}.source")
        timestamp = group.get("timestamp")
        if timestamp is not None:
            parse_iso_datetime(
                get_required_string(group, "timestamp", f"{path}.timestamp"),
                f"{path}.timestamp",
            )
