from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from hermes_finance._brief_utils import (
    NEWS_FRESHNESS_WINDOW_DAYS,
    QUOTE_FRESHNESS_WINDOW,
    ensure_mapping,
    normalize_ticker,
    parse_iso_datetime,
)
from hermes_finance._brief_validation import EvidenceSnapshotValidator
from hermes_finance._strategy_validation import StrategySnapshotValidator

AdapterStatus = Literal["complete", "partial", "failed"]
DiagnosticType = Literal[
    "provider_error",
    "missing_field",
    "missing_provenance",
    "malformed_payload",
    "partial_payload",
    "stale_timestamp",
    "future_timestamp",
    "invalid_timestamp",
    "invalid_symbol",
    "unsupported_symbol",
    "symbol_mismatch",
    "skipped_evidence_group",
    "unknown_evidence_group",
]

KNOWN_GROUPS = (
    "market_context",
    "quotes",
    "ranges",
    "support_levels",
    "news",
    "moving_averages",
    "momentum",
    "range_52w",
    "support_resistance",
    "volatility",
    "volume",
)
BRIEF_GROUPS = ("market_context", "quotes", "ranges", "support_levels", "news")
STRATEGY_GROUPS = (
    "quotes",
    "moving_averages",
    "momentum",
    "range_52w",
    "support_resistance",
    "volatility",
    "volume",
)
STRATEGY_FRESHNESS_WINDOW = timedelta(days=NEWS_FRESHNESS_WINDOW_DAYS)


@dataclass(frozen=True)
class AdapterDiagnostic:
    type: DiagnosticType
    message: str
    symbol: str | None = None
    field: str | None = None


@dataclass(frozen=True)
class AdapterResult:
    fixture: dict[str, object] | None
    status: AdapterStatus
    diagnostics: list[AdapterDiagnostic]
    provider: str
    as_of: str


def map_daily_market_brief_evidence(
    watchlist: list[str],
    as_of: str,
    provider: str,
    payloads: Mapping[str, object],
) -> AdapterResult:
    adapter = _EvidenceAdapter(
        watchlist=watchlist,
        as_of=as_of,
        provider=provider,
        payloads=payloads,
    )
    return adapter.map_brief()


def map_entry_zone_strategy_evidence(
    watchlist: list[str],
    as_of: str,
    provider: str,
    payloads: Mapping[str, object],
) -> AdapterResult:
    adapter = _EvidenceAdapter(
        watchlist=watchlist,
        as_of=as_of,
        provider=provider,
        payloads=payloads,
    )
    return adapter.map_strategy()


class _EvidenceAdapter:
    def __init__(
        self,
        *,
        watchlist: list[str],
        as_of: str,
        provider: str,
        payloads: Mapping[str, object],
    ) -> None:
        self._watchlist = watchlist
        self._normalized_watchlist = [normalize_ticker(symbol) for symbol in watchlist]
        self._provider = provider
        self._as_of = as_of
        self._payloads = payloads
        self._diagnostics: list[AdapterDiagnostic] = []
        self._as_of_dt: datetime | None = None

    def map_brief(self) -> AdapterResult:
        if not self._prepare():
            return self._build_result(None)

        fixture: dict[str, object] = {
            "as_of": self._as_of,
            "market_context": {"indices": [], "notes": []},
            "tickers": {},
        }
        tickers = self._brief_tickers(fixture)
        invalid_inputs: dict[str, str] = {}

        self._collect_group_diagnostics(BRIEF_GROUPS)
        self._map_market_context(fixture)
        self._map_quotes(tickers, invalid_inputs)
        self._map_ranges(tickers, invalid_inputs)
        self._map_support_levels(tickers, invalid_inputs)
        self._map_news(tickers, invalid_inputs)

        if invalid_inputs:
            fixture["invalid_inputs"] = invalid_inputs

        return self._validated_brief_result(fixture)

    def map_strategy(self) -> AdapterResult:
        if not self._prepare():
            return self._build_result(None)

        fixture: dict[str, object] = {"as_of": self._as_of, "tickers": {}}
        tickers = self._strategy_tickers(fixture)
        invalid_inputs: dict[str, str] = {}

        self._collect_group_diagnostics(STRATEGY_GROUPS)
        self._map_quotes(tickers, invalid_inputs)
        self._map_strategy_group(
            tickers,
            invalid_inputs,
            "moving_averages",
            ("sma_50", "sma_200"),
            STRATEGY_FRESHNESS_WINDOW,
        )
        self._map_strategy_group(
            tickers,
            invalid_inputs,
            "momentum",
            ("rsi_14",),
            STRATEGY_FRESHNESS_WINDOW,
        )
        self._map_strategy_group(
            tickers,
            invalid_inputs,
            "range_52w",
            ("low", "high"),
            STRATEGY_FRESHNESS_WINDOW,
        )
        self._map_strategy_group(
            tickers,
            invalid_inputs,
            "support_resistance",
            ("support_1", "resistance_1"),
            STRATEGY_FRESHNESS_WINDOW,
        )
        self._map_strategy_group(
            tickers,
            invalid_inputs,
            "volatility",
            ("atr_14",),
            STRATEGY_FRESHNESS_WINDOW,
        )
        self._map_strategy_group(
            tickers,
            invalid_inputs,
            "volume",
            ("latest_volume", "avg_volume_20d"),
            STRATEGY_FRESHNESS_WINDOW,
        )

        if invalid_inputs:
            fixture["invalid_inputs"] = invalid_inputs

        return self._validated_strategy_result(fixture)

    def _prepare(self) -> bool:
        if not isinstance(self._payloads, Mapping):
            self._append(
                "malformed_payload",
                "payloads must be a mapping of evidence groups",
                field="payloads",
            )
            return False
        try:
            self._as_of_dt = parse_iso_datetime(self._as_of, "as_of")
        except ValueError as exc:
            self._append(
                "invalid_timestamp",
                str(exc),
                field="as_of",
            )
            return False
        return True

    def _collect_group_diagnostics(self, supported_groups: Sequence[str]) -> None:
        supported = set(supported_groups)
        for group in sorted(self._payloads):
            if group not in KNOWN_GROUPS:
                self._append(
                    "unknown_evidence_group",
                    f"evidence group {group} is unknown and was ignored",
                    field=group,
                )
            elif group not in supported:
                self._append(
                    "skipped_evidence_group",
                    f"evidence group {group} is not used for this adapter",
                    field=group,
                )

    def _map_market_context(self, fixture: dict[str, object]) -> None:
        raw_group = self._payloads.get("market_context")
        if raw_group is None:
            self._append(
                "partial_payload",
                "market_context payload group is missing",
                field="market_context",
            )
            return
        if not isinstance(raw_group, Mapping):
            self._append(
                "malformed_payload",
                "market_context payload group must be a mapping",
                field="market_context",
            )
            return

        indices: list[dict[str, object]] = []
        notes: list[dict[str, object]] = []
        for proxy_key in sorted(raw_group):
            raw_entry = raw_group[proxy_key]
            if proxy_key == "notes":
                parsed_notes = self._map_market_notes(raw_entry)
                notes.extend(parsed_notes)
                continue
            entry = self._map_market_index(proxy_key, raw_entry)
            if entry is not None:
                indices.append(entry)

        market_context = ensure_mapping(fixture["market_context"], "market_context")
        market_context["indices"] = indices
        market_context["notes"] = notes

    def _map_market_notes(self, raw_entry: object) -> list[dict[str, object]]:
        if not isinstance(raw_entry, Sequence) or isinstance(raw_entry, (str, bytes)):
            self._append(
                "malformed_payload",
                "market_context notes payload must be a list",
                field="market_context.notes",
            )
            return []
        notes: list[dict[str, object]] = []
        for index, raw_note in enumerate(raw_entry):
            path = f"market_context.notes[{index}]"
            if not isinstance(raw_note, Mapping):
                self._append(
                    "malformed_payload",
                    f"{path} must be a mapping",
                    field=path,
                )
                continue
            note = self._timestamped_payload(
                raw_note,
                field_path=path,
                required_fields=("headline",),
                freshness_window=STRATEGY_FRESHNESS_WINDOW,
                drop_on_missing_timestamp=True,
                drop_on_invalid_timestamp=True,
            )
            if note is None:
                continue
            notes.append(note)
        return notes

    def _map_market_index(
        self,
        proxy_key: str,
        raw_entry: object,
    ) -> dict[str, object] | None:
        path = f"market_context.{proxy_key}"
        if not isinstance(raw_entry, Mapping):
            self._append(
                "malformed_payload",
                f"{path} must be a mapping",
                field=path,
            )
            return None
        entry = self._timestamped_payload(
            raw_entry,
            field_path=path,
            required_fields=("name", "price", "change_percent"),
            freshness_window=QUOTE_FRESHNESS_WINDOW,
            drop_on_missing_timestamp=True,
            drop_on_invalid_timestamp=True,
        )
        if entry is None:
            return None
        entry["symbol"] = self._market_context_symbol(proxy_key, raw_entry)
        return entry

    def _map_quotes(
        self,
        tickers: dict[str, dict[str, object]],
        invalid_inputs: dict[str, str],
    ) -> None:
        raw_group = self._payloads.get("quotes")
        if raw_group is None:
            self._append(
                "partial_payload",
                "quotes payload group is missing",
                field="quotes",
            )
            return
        group = self._symbol_group(raw_group, "quotes")
        if group is None:
            return

        for symbol in self._normalized_watchlist:
            raw_entry = group.get(symbol)
            if raw_entry is None:
                self._append(
                    "partial_payload",
                    f"quotes payload is missing for {symbol}",
                    symbol=symbol,
                    field="quotes",
                )
                continue
            if not isinstance(raw_entry, Mapping):
                self._append(
                    "malformed_payload",
                    f"quotes payload for {symbol} must be a mapping",
                    symbol=symbol,
                    field="quotes",
                )
                continue
            classified = self._classify_symbol_entry(symbol, "quotes", raw_entry)
            if classified == "invalid":
                invalid_inputs[symbol] = self._invalid_reason(raw_entry, symbol)
                tickers.pop(symbol, None)
                continue
            if classified == "unsupported":
                invalid_inputs[symbol] = self._invalid_reason(raw_entry, symbol)
                tickers.pop(symbol, None)
                continue
            if classified == "error":
                continue

            payload = self._timestamped_payload(
                raw_entry,
                field_path="quotes." + symbol,
                required_fields=("current_price",),
                freshness_window=QUOTE_FRESHNESS_WINDOW,
            )
            if payload is None:
                continue
            company_name = raw_entry.get("company_name")
            if isinstance(company_name, str):
                tickers.setdefault(symbol, {})["company_name"] = company_name
            tickers.setdefault(symbol, {})["quote"] = payload

    def _map_ranges(
        self,
        tickers: dict[str, dict[str, object]],
        invalid_inputs: dict[str, str],
    ) -> None:
        self._map_symbol_group(
            tickers,
            invalid_inputs,
            group_name="ranges",
            canonical_name="range_20d",
            required_fields=("recent_low_20d", "recent_high_20d"),
            freshness_window=QUOTE_FRESHNESS_WINDOW,
        )

    def _map_support_levels(
        self,
        tickers: dict[str, dict[str, object]],
        invalid_inputs: dict[str, str],
    ) -> None:
        self._map_symbol_group(
            tickers,
            invalid_inputs,
            group_name="support_levels",
            canonical_name="support_level",
            required_fields=("price",),
            freshness_window=QUOTE_FRESHNESS_WINDOW,
        )

    def _map_news(
        self,
        tickers: dict[str, dict[str, object]],
        invalid_inputs: dict[str, str],
    ) -> None:
        raw_group = self._payloads.get("news")
        if raw_group is None:
            self._append(
                "partial_payload",
                "news payload group is missing",
                field="news",
            )
            return
        group = self._symbol_group(raw_group, "news")
        if group is None:
            return

        for symbol in self._normalized_watchlist:
            if symbol in invalid_inputs:
                continue
            raw_entry = group.get(symbol)
            if raw_entry is None:
                self._append(
                    "partial_payload",
                    f"news payload is missing for {symbol}",
                    symbol=symbol,
                    field="news",
                )
                continue
            if isinstance(raw_entry, Mapping):
                classified = self._classify_symbol_entry(symbol, "news", raw_entry)
                if classified in {"invalid", "unsupported"}:
                    invalid_inputs[symbol] = self._invalid_reason(raw_entry, symbol)
                    tickers.pop(symbol, None)
                    continue
                if classified == "error":
                    continue
            if not isinstance(raw_entry, Sequence) or isinstance(
                raw_entry, (str, bytes)
            ):
                self._append(
                    "malformed_payload",
                    f"news payload for {symbol} must be a list",
                    symbol=symbol,
                    field="news",
                )
                continue

            articles: list[dict[str, object]] = []
            for index, item in enumerate(raw_entry):
                if not isinstance(item, Mapping):
                    self._append(
                        "malformed_payload",
                        f"news payload item {index} for {symbol} must be a mapping",
                        symbol=symbol,
                        field="news",
                    )
                    continue
                article = self._timestamped_payload(
                    item,
                    field_path=f"news.{symbol}[{index}]",
                    required_fields=("headline", "summary"),
                    freshness_window=STRATEGY_FRESHNESS_WINDOW,
                )
                if article is not None:
                    articles.append(article)
            tickers.setdefault(symbol, {})["news"] = articles

    def _map_strategy_group(
        self,
        tickers: dict[str, dict[str, object]],
        invalid_inputs: dict[str, str],
        group_name: str,
        required_fields: Sequence[str],
        freshness_window: timedelta,
    ) -> None:
        self._map_symbol_group(
            tickers,
            invalid_inputs,
            group_name=group_name,
            canonical_name=group_name,
            required_fields=required_fields,
            freshness_window=freshness_window,
            strategy=True,
        )

    def _map_symbol_group(
        self,
        tickers: dict[str, dict[str, object]],
        invalid_inputs: dict[str, str],
        *,
        group_name: str,
        canonical_name: str,
        required_fields: Sequence[str],
        freshness_window: timedelta,
        strategy: bool = False,
    ) -> None:
        raw_group = self._payloads.get(group_name)
        if raw_group is None:
            self._append(
                "partial_payload",
                f"{group_name} payload group is missing",
                field=group_name,
            )
            return
        group = self._symbol_group(raw_group, group_name)
        if group is None:
            return

        for symbol in self._normalized_watchlist:
            if symbol in invalid_inputs:
                continue
            raw_entry = group.get(symbol)
            if raw_entry is None:
                self._append(
                    "partial_payload",
                    f"{group_name} payload is missing for {symbol}",
                    symbol=symbol,
                    field=group_name,
                )
                continue
            payload = self._symbol_payload(
                symbol,
                group_name,
                raw_entry,
                required_fields=required_fields,
                freshness_window=freshness_window,
            )
            if payload is None:
                classified = raw_entry if isinstance(raw_entry, Mapping) else None
                if isinstance(classified, Mapping):
                    status = classified.get("status")
                    if status == "invalid_symbol":
                        invalid_inputs[symbol] = self._invalid_reason(
                            classified, symbol
                        )
                        tickers.pop(symbol, None)
                    elif status == "unsupported_symbol":
                        invalid_inputs[symbol] = self._invalid_reason(
                            classified, symbol
                        )
                        tickers.pop(symbol, None)
                continue
            ticker = tickers.setdefault(symbol, {})
            if strategy:
                target = ensure_mapping(ticker.setdefault("strategy", {}), "strategy")
                target[canonical_name] = payload
            else:
                ticker[canonical_name] = payload

    def _symbol_payload(
        self,
        symbol: str,
        group_name: str,
        raw_entry: object,
        *,
        required_fields: Sequence[str],
        freshness_window: timedelta,
    ) -> dict[str, object] | None:
        if not isinstance(raw_entry, Mapping):
            self._append(
                "malformed_payload",
                f"{group_name} payload for {symbol} must be a mapping",
                symbol=symbol,
                field=group_name,
            )
            return None

        classified = self._classify_symbol_entry(symbol, group_name, raw_entry)
        if classified != "ok":
            return None

        return self._timestamped_payload(
            raw_entry,
            field_path=f"{group_name}.{symbol}",
            required_fields=required_fields,
            freshness_window=freshness_window,
        )

    def _timestamped_payload(
        self,
        raw_entry: Mapping[str, object],
        *,
        field_path: str,
        required_fields: Sequence[str],
        freshness_window: timedelta,
        drop_on_missing_timestamp: bool = False,
        drop_on_invalid_timestamp: bool = False,
    ) -> dict[str, object] | None:
        source = raw_entry.get("source")
        if not isinstance(source, str) or not source:
            self._append(
                "missing_provenance",
                f"{field_path} is missing source provenance",
                field=f"{field_path}.source",
            )
            return None

        payload: dict[str, object] = {"source": self._canonical_source()}
        for field in required_fields:
            if field not in raw_entry:
                self._append(
                    "missing_field",
                    f"{field_path} is missing required field {field}",
                    field=f"{field_path}.{field}",
                )
                return None
            payload[field] = raw_entry[field]

        if "timestamp" not in raw_entry:
            self._append(
                "missing_field",
                f"{field_path} is missing required field timestamp",
                field=f"{field_path}.timestamp",
            )
            if drop_on_missing_timestamp:
                return None
            return payload

        timestamp = raw_entry.get("timestamp")
        if not isinstance(timestamp, str):
            self._append(
                "invalid_timestamp",
                f"{field_path}.timestamp must be an ISO-8601 string",
                field=f"{field_path}.timestamp",
            )
            if drop_on_invalid_timestamp:
                return None
            return payload

        try:
            parsed = parse_iso_datetime(timestamp, f"{field_path}.timestamp")
        except ValueError as exc:
            self._append(
                "invalid_timestamp",
                str(exc),
                field=f"{field_path}.timestamp",
            )
            if drop_on_invalid_timestamp:
                return None
            return payload

        payload["timestamp"] = timestamp
        assert self._as_of_dt is not None
        if parsed > self._as_of_dt:
            self._append(
                "future_timestamp",
                f"{field_path} timestamp is later than as_of",
                field=f"{field_path}.timestamp",
            )
        elif freshness_window == STRATEGY_FRESHNESS_WINDOW:
            age_days = (self._as_of_dt.date() - parsed.date()).days
            if age_days > NEWS_FRESHNESS_WINDOW_DAYS:
                self._append(
                    "stale_timestamp",
                    f"{field_path} timestamp is stale",
                    field=f"{field_path}.timestamp",
                )
        elif self._as_of_dt - parsed > freshness_window:
            self._append(
                "stale_timestamp",
                f"{field_path} timestamp is stale",
                field=f"{field_path}.timestamp",
            )
        return payload

    def _symbol_group(
        self,
        raw_group: object,
        group_name: str,
    ) -> Mapping[str, object] | None:
        if not isinstance(raw_group, Mapping):
            self._append(
                "malformed_payload",
                f"{group_name} payload group must be a mapping",
                field=group_name,
            )
            return None
        normalized_group: dict[str, object] = {}
        for key, value in raw_group.items():
            if not isinstance(key, str):
                self._append(
                    "malformed_payload",
                    f"{group_name} payload keys must be strings",
                    field=group_name,
                )
                return None
            normalized_group[normalize_ticker(key)] = value
        return normalized_group

    def _classify_symbol_entry(
        self,
        requested_symbol: str,
        group_name: str,
        raw_entry: Mapping[str, object],
    ) -> Literal["ok", "invalid", "unsupported", "error"]:
        status = raw_entry.get("status", "ok")
        if status == "error":
            message = raw_entry.get("message")
            rendered = (
                message
                if isinstance(message, str) and message
                else f"{group_name} provider error for {requested_symbol}"
            )
            self._append(
                "provider_error",
                rendered,
                symbol=requested_symbol,
                field=group_name,
            )
            return "error"
        if status == "invalid_symbol":
            self._append(
                "invalid_symbol",
                self._invalid_reason(raw_entry, requested_symbol),
                symbol=requested_symbol,
                field=group_name,
            )
            return "invalid"
        if status == "unsupported_symbol":
            self._append(
                "unsupported_symbol",
                self._invalid_reason(raw_entry, requested_symbol),
                symbol=requested_symbol,
                field=group_name,
            )
            return "unsupported"

        raw_symbol = raw_entry.get("symbol")
        if raw_symbol is None:
            return "ok"
        if not isinstance(raw_symbol, str):
            self._append(
                "malformed_payload",
                (
                    f"{group_name} payload symbol for {requested_symbol} must "
                    "be a string when present"
                ),
                symbol=requested_symbol,
                field=f"{group_name}.symbol",
            )
            return "error"
        if normalize_ticker(raw_symbol) != requested_symbol:
            self._append(
                "symbol_mismatch",
                (
                    f"{group_name} payload symbol {normalize_ticker(raw_symbol)} "
                    f"does not match requested symbol {requested_symbol}"
                ),
                symbol=requested_symbol,
                field=f"{group_name}.symbol",
            )
            return "error"
        return "ok"

    def _invalid_reason(
        self,
        raw_entry: Mapping[str, object],
        symbol: str,
    ) -> str:
        message = raw_entry.get("message")
        if isinstance(message, str) and message:
            return message
        status = raw_entry.get("status")
        if status == "invalid_symbol":
            return f"Provider flagged {symbol} as invalid"
        return f"Provider does not support {symbol}"

    def _canonical_source(self) -> str:
        return f"recorded:{self._provider}"

    def _market_context_symbol(
        self,
        proxy_key: str,
        raw_entry: Mapping[str, object],
    ) -> str:
        raw_symbol = raw_entry.get("symbol")
        if isinstance(raw_symbol, str) and raw_symbol:
            return normalize_ticker(raw_symbol)
        return normalize_ticker(proxy_key)

    def _brief_tickers(
        self,
        fixture: dict[str, object],
    ) -> dict[str, dict[str, object]]:
        tickers = ensure_mapping(fixture["tickers"], "tickers")
        return tickers  # type: ignore[return-value]

    def _strategy_tickers(
        self,
        fixture: dict[str, object],
    ) -> dict[str, dict[str, object]]:
        tickers = ensure_mapping(fixture["tickers"], "tickers")
        return tickers  # type: ignore[return-value]

    def _validated_brief_result(self, fixture: dict[str, object]) -> AdapterResult:
        try:
            EvidenceSnapshotValidator().validate(fixture, self._as_of)
        except ValueError as exc:
            self._append(
                "malformed_payload",
                f"adapter output failed brief validation: {exc}",
                field="fixture",
            )
            return self._build_result(None)
        return self._build_result(fixture)

    def _validated_strategy_result(self, fixture: dict[str, object]) -> AdapterResult:
        try:
            StrategySnapshotValidator().validate(fixture, self._as_of)
        except ValueError as exc:
            self._append(
                "malformed_payload",
                f"adapter output failed strategy validation: {exc}",
                field="fixture",
            )
            return self._build_result(None)
        return self._build_result(fixture)

    def _build_result(self, fixture: dict[str, object] | None) -> AdapterResult:
        status: AdapterStatus
        if fixture is None:
            status = "failed"
        elif self._diagnostics:
            status = "partial"
        else:
            status = "complete"
        return AdapterResult(
            fixture=fixture,
            status=status,
            diagnostics=list(self._diagnostics),
            provider=self._provider,
            as_of=self._as_of,
        )

    def _append(
        self,
        diagnostic_type: DiagnosticType,
        message: str,
        *,
        symbol: str | None = None,
        field: str | None = None,
    ) -> None:
        self._diagnostics.append(
            AdapterDiagnostic(
                type=diagnostic_type,
                message=message,
                symbol=symbol,
                field=field,
            )
        )
