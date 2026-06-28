from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from hermes_finance._brief_utils import (
    LIMITATIONS_SENTENCE,
    QUOTE_FRESHNESS_WINDOW,
    assert_report_language,
    freshness_status,
)
from hermes_finance._strategy_scoring import (
    StrategyEvaluation,
    strategy_freshness_status,
)


class StrategyMarkdownRenderer:
    def render_validation_failure(self, as_of: str, reason: str) -> str:
        return (
            "\n\n".join(
                [
                    f"# Entry-Zone Strategy ({as_of})",
                    "## Validation Failure",
                    "Deterministic Narrative",
                    reason,
                    self.render_limitations(),
                ]
            )
            + "\n"
        )

    def render_method_summary(self) -> str:
        return "\n".join(
            [
                "## Method Summary",
                "Deterministic Narrative",
                (
                    "- Technical setup score weights: trend 25, "
                    "pullback and location 25, momentum 20, "
                    "volume 15, volatility 15."
                ),
                (
                    "- Label thresholds: 75 to 100 High-scoring research "
                    "candidate; 60 to 74 Constructive research candidate; "
                    "45 to 59 Mixed research candidate; 0 to 44 Weak "
                    "research candidate."
                ),
                (
                    "- Missing, stale, invalid, or future-dated required "
                    "evidence produces the visible label Insufficient fresh "
                    "evidence and removes score, rank, and observation-zone "
                    "evaluation for that ticker."
                ),
            ]
        )

    def render_watchlist_summary(
        self,
        watchlist: list[str],
        supported: list[str],
        duplicates: list[str],
        ambiguous: list[tuple[str, str, str]],
        unsupported: list[tuple[str, str]],
        evaluations: Mapping[str, StrategyEvaluation],
    ) -> str:
        scored_count = sum(
            1 for symbol in supported if evaluations[symbol].score_breakdown is not None
        )
        insufficient_count = sum(
            1 for symbol in supported if evaluations[symbol].score_breakdown is None
        )
        ambiguous_text = (
            ", ".join(f"{normalized} ({reason})" for _, normalized, reason in ambiguous)
            if ambiguous
            else "none"
        )
        unsupported_text = (
            ", ".join(normalized for _, normalized in unsupported)
            if unsupported
            else "none"
        )
        return "\n".join(
            [
                "## Watchlist Coverage Summary",
                "Deterministic Narrative",
                f"- Raw inputs: {', '.join(watchlist)}.",
                (
                    "- Supported unique normalized tickers: "
                    f"{', '.join(supported) if supported else 'none'}."
                ),
                (
                    "- Duplicate normalized tickers skipped after first "
                    f"occurrence: {', '.join(duplicates) if duplicates else 'none'}."
                ),
                f"- Ambiguous inputs: {ambiguous_text}.",
                f"- Unsupported inputs: {unsupported_text}.",
                (
                    f"- Counts: supported {len(supported)}, duplicates "
                    f"{len(duplicates)}, unsupported {len(unsupported)}, "
                    f"ambiguous {len(ambiguous)}, scored {scored_count}, "
                    f"insufficient_evidence {insufficient_count}."
                ),
            ]
        )

    def render_comparison_table(
        self,
        ranked_symbols: list[str],
        supported: list[str],
        evaluations: Mapping[str, StrategyEvaluation],
    ) -> str:
        lines = [
            "## Comparison Table",
            "Deterministic Calculation",
            "| Rank | Ticker | Label | Technical Setup Score | Observation Zone |",
            "| --- | --- | --- | --- | --- |",
        ]
        rank = 1
        for symbol in ranked_symbols:
            evaluation = evaluations[symbol]
            if evaluation.score_breakdown is not None:
                score_text = str(evaluation.score_breakdown.total)
                rank_text = str(rank)
                rank += 1
            else:
                score_text = "not scored"
                rank_text = "-"
            observation_text = (
                f"{evaluation.observation_zone.lower:.2f} "
                f"to {evaluation.observation_zone.upper:.2f}"
                if evaluation.observation_zone.evaluated
                else "not evaluated"
            )
            lines.append(
                f"| {rank_text} | {symbol} | {evaluation.label} | "
                f"{score_text} | {observation_text} |"
            )

        if not supported:
            lines.append("| - | none | none | none | none |")
        return "\n".join(lines)

    def render_supported_ticker(
        self,
        symbol: str,
        payload: Mapping[str, object],
        as_of_dt: datetime,
        evaluation: StrategyEvaluation,
    ) -> str:
        company_name = evaluation.company_name
        title = f"## {symbol}"
        if company_name:
            title = f"## {symbol} - {company_name}"

        lines = [title, "Evidence"]
        lines.append(self._render_quote_line(payload.get("quote"), as_of_dt))
        lines.append(
            self._render_strategy_group_line(
                "Moving averages", payload, "moving_averages", as_of_dt
            )
        )
        lines.append(
            self._render_strategy_group_line("Momentum", payload, "momentum", as_of_dt)
        )
        lines.append(
            self._render_strategy_group_line(
                "52-week range", payload, "range_52w", as_of_dt
            )
        )
        lines.append(
            self._render_strategy_group_line(
                "Support and resistance", payload, "support_resistance", as_of_dt
            )
        )
        lines.append(
            self._render_strategy_group_line(
                "Volatility", payload, "volatility", as_of_dt
            )
        )
        lines.append(
            self._render_strategy_group_line("Volume", payload, "volume", as_of_dt)
        )
        lines.extend(self._render_calculation(symbol, evaluation))
        lines.extend(self._render_conflicts(evaluation))
        lines.extend(self._render_narrative(evaluation))
        return "\n".join(lines)

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
                (
                    "The strategy report does not substitute another ticker "
                    "for an ambiguous input."
                ),
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
                "The strategy report does not invent unsupported ticker evidence.",
            ]
        )

    def render_limitations(self) -> str:
        return "\n".join(
            [
                "## Limitations",
                LIMITATIONS_SENTENCE,
                "Deterministic Narrative",
                (
                    "The strategy report is fixture-backed, "
                    "template-rendered, and limited to the supplied evidence "
                    "and spec-defined calculations."
                ),
            ]
        )

    def assert_language(self, report: str) -> None:
        assert_report_language(report)

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

    def _render_strategy_group_line(
        self,
        title: str,
        payload: Mapping[str, object],
        group_name: str,
        as_of_dt: datetime,
    ) -> str:
        strategy = payload.get("strategy")
        if not isinstance(strategy, Mapping):
            return f"- {title}: unavailable."
        group = strategy.get(group_name)
        if not isinstance(group, Mapping):
            return f"- {title}: unavailable."
        freshness = strategy_freshness_status(group.get("timestamp"), as_of_dt)
        values = ", ".join(
            f"{key} {value}"
            for key, value in group.items()
            if key not in {"timestamp", "source"}
        )
        return (
            f"- {title}: {values}, "
            f"timestamp {group.get('timestamp') or 'missing'}, "
            f"source {group.get('source', 'missing')}, "
            f"freshness {freshness}."
        )

    def _render_calculation(
        self, symbol: str, evaluation: StrategyEvaluation
    ) -> list[str]:
        lines = ["Deterministic Calculation"]
        if evaluation.score_breakdown is None:
            lines.append("- Technical setup score: not evaluated.")
            lines.append(f"- Research-candidate label: {evaluation.label}.")
            for reason in evaluation.insufficient_reasons:
                lines.append(f"- Insufficient evidence reason: {reason}.")
        else:
            breakdown = evaluation.score_breakdown
            lines.append(
                f"- Technical setup score for {symbol}: {breakdown.total}/100."
            )
            lines.append(f"- Trend quality: {breakdown.trend_quality}/25.")
            lines.append(
                "- Pullback and location quality: "
                f"{breakdown.pullback_location_quality}/25."
            )
            lines.append(f"- Momentum quality: {breakdown.momentum_quality}/20.")
            lines.append(f"- Volume quality: {breakdown.volume_quality}/15.")
            lines.append(f"- Volatility quality: {breakdown.volatility_quality}/15.")
            lines.append(f"- Research-candidate label: {evaluation.label}.")

        if evaluation.observation_zone.evaluated:
            lines.append(
                f"- Observation zone: {evaluation.observation_zone.lower:.2f} "
                f"to {evaluation.observation_zone.upper:.2f}."
            )
        else:
            lines.append(
                "- Observation zone not evaluated: "
                f"{evaluation.observation_zone.reason}."
            )
        return lines

    def _render_conflicts(self, evaluation: StrategyEvaluation) -> list[str]:
        lines = ["### Conflict Notes"]
        if evaluation.conflict_notes:
            for note in evaluation.conflict_notes:
                lines.append(f"- {note}")
        else:
            lines.append("- none")
        return lines

    def _render_narrative(self, evaluation: StrategyEvaluation) -> list[str]:
        lines = ["Deterministic Narrative"]
        if evaluation.score_breakdown is None:
            lines.append(
                "This ticker remains unscored because required fresh strategy "
                "evidence is incomplete or invalid under the spec-defined "
                "checks."
            )
        elif evaluation.conflict_notes:
            lines.append(
                "The score remains deterministic, but the report surfaces "
                "conflicting supplied signals instead of hiding uncertainty."
            )
        else:
            lines.append(
                "The score and observation zone come only from supplied "
                "evidence and deterministic calculations under the accepted "
                "strategy rubric."
            )
        return lines
