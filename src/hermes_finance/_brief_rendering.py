from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime

from hermes_finance._brief_utils import (
    LIMITATIONS_SENTENCE,
    QUOTE_FRESHNESS_WINDOW,
    freshness_status,
    news_freshness_status,
    parse_iso_datetime,
)
from hermes_finance._pullback import PullbackEvaluator


class MarkdownRenderer:
    def __init__(self, pullback_evaluator: PullbackEvaluator | None = None) -> None:
        self._pullback_evaluator = pullback_evaluator or PullbackEvaluator()

    def render_validation_failure(self, as_of: str, reason: str) -> str:
        parsed_as_of = parse_iso_datetime(as_of, "as_of")
        return "\n\n".join(
            [
                f"# Daily Market Brief ({parsed_as_of.isoformat()})",
                "## Validation Failure",
                "Deterministic Narrative",
                reason,
                self.render_limitations(),
            ]
        ) + "\n"

    def render_market_context(
        self,
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
            freshness = freshness_status(
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
                freshness = news_freshness_status(note.get("timestamp"), as_of_dt)
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

    def render_watchlist_summary(
        self,
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

    def render_supported_ticker(
        self,
        symbol: str,
        payload: Mapping[str, object],
        as_of_dt: datetime,
    ) -> str:
        company_name = payload.get("company_name")
        title = f"## {symbol}"
        if isinstance(company_name, str) and company_name.strip():
            title = f"## {symbol} - {company_name}"

        lines = [title, "Evidence"]
        lines.append(self._render_quote_line(payload.get("quote"), as_of_dt))
        lines.append(self._render_range_line(payload.get("range_20d"), as_of_dt))
        lines.append(self._render_support_line(payload.get("support_level"), as_of_dt))
        lines.extend(self._render_news(payload.get("news"), as_of_dt))
        lines.extend(self.render_pullback_zone(symbol, payload, as_of_dt))
        lines.extend(
            [
                "Deterministic Narrative",
                "This section restates only supplied fixture evidence and "
                "deterministic freshness or zone outcomes.",
            ]
        )
        return "\n".join(lines)

    def render_pullback_zone(
        self,
        symbol: str,
        payload: Mapping[str, object],
        as_of_dt: datetime,
    ) -> list[str]:
        lines = ["### Research-Only Pullback Zone", "Deterministic Calculation"]
        result = self._pullback_evaluator.evaluate(payload, as_of_dt)
        if result.status == "evaluated":
            lines.append(
                f"- Candidate zone for {symbol}: "
                f"{result.lower:.2f} to {result.upper:.2f}."
            )
            lines.append(
                "- Reference price source: "
                f"{result.reference_source}; "
                f"reference timestamp {result.reference_timestamp}."
            )
        else:
            lines.append(f"- Pullback zone not evaluated: {result.reason}.")
        return lines

    def render_ambiguous_section(
        self, raw_symbol: str, normalized: str, reason: str
    ) -> str:
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

    def render_unsupported_section(self, raw_symbol: str, normalized: str) -> str:
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

    def render_limitations(self) -> str:
        return "\n".join(
            [
                "## Limitations",
                LIMITATIONS_SENTENCE,
                "Deterministic Narrative",
                "The report is fixture-backed, template-rendered, and limited to "
                "the supplied evidence.",
            ]
        )

    def _render_quote_line(self, quote: object, as_of_dt: datetime) -> str:
        if not isinstance(quote, Mapping):
            return "- Quote: unavailable."
        timestamp = quote.get("timestamp")
        freshness = freshness_status(timestamp, as_of_dt, QUOTE_FRESHNESS_WINDOW)
        return (
            "- Quote: "
            f"current_price {quote.get('current_price')}, "
            f"timestamp {timestamp or 'missing'}, "
            f"source {quote.get('source', 'missing')}, "
            f"freshness {freshness}."
        )

    def _render_range_line(self, range_data: object, as_of_dt: datetime) -> str:
        if not isinstance(range_data, Mapping):
            return "- 20-day range: unavailable."
        timestamp = range_data.get("timestamp")
        freshness = freshness_status(timestamp, as_of_dt, QUOTE_FRESHNESS_WINDOW)
        return (
            "- 20-day range: "
            f"recent_low_20d {range_data.get('recent_low_20d')}, "
            f"recent_high_20d {range_data.get('recent_high_20d')}, "
            f"timestamp {timestamp or 'missing'}, "
            f"source {range_data.get('source', 'missing')}, "
            f"freshness {freshness}."
        )

    def _render_support_line(self, support_level: object, as_of_dt: datetime) -> str:
        if not isinstance(support_level, Mapping):
            return "- Support level: unavailable."
        timestamp = support_level.get("timestamp")
        freshness = freshness_status(timestamp, as_of_dt, QUOTE_FRESHNESS_WINDOW)
        return (
            "- Support level: "
            f"price {support_level.get('price')}, "
            f"timestamp {timestamp or 'missing'}, "
            f"source {support_level.get('source', 'missing')}, "
            f"freshness {freshness}."
        )

    def _render_news(self, news_items: object, as_of_dt: datetime) -> list[str]:
        if not isinstance(news_items, Sequence) or isinstance(news_items, (str, bytes)):
            return ["- News: unavailable."]
        if not news_items:
            return ["- News: unavailable."]

        lines: list[str] = []
        for item in news_items:
            if not isinstance(item, Mapping):
                continue
            freshness = news_freshness_status(item.get("timestamp"), as_of_dt)
            lines.append(
                "- News item: "
                f"{item.get('headline')}; summary {item.get('summary')}; "
                f"timestamp {item.get('timestamp') or 'missing'}, "
                f"source {item.get('source')}, "
                f"freshness {freshness}."
            )
        return lines or ["- News: unavailable."]
