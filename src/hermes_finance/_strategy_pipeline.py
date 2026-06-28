from __future__ import annotations

from hermes_finance._brief_utils import normalize_ticker
from hermes_finance._strategy_rendering import StrategyMarkdownRenderer
from hermes_finance._strategy_scoring import StrategyScorer
from hermes_finance._strategy_validation import StrategySnapshotValidator


class EntryZoneStrategyPipeline:
    def __init__(
        self,
        validator: StrategySnapshotValidator | None = None,
        scorer: StrategyScorer | None = None,
        renderer: StrategyMarkdownRenderer | None = None,
    ) -> None:
        self._validator = validator or StrategySnapshotValidator()
        self._scorer = scorer or StrategyScorer()
        self._renderer = renderer or StrategyMarkdownRenderer()

    def generate(self, watchlist: list[str], as_of: str, fixture: dict) -> str:
        if not isinstance(watchlist, list):
            raise ValueError("watchlist must be a list[str]")
        if not watchlist:
            return self._renderer.render_validation_failure(
                as_of, "Watchlist is empty."
            )

        snapshot = self._validator.validate(fixture, as_of)

        supported: list[str] = []
        duplicates: list[str] = []
        ambiguous: list[tuple[str, str, str]] = []
        unsupported: list[tuple[str, str]] = []
        ordered_sections: list[tuple[str, str, str | None, str | None]] = []
        seen_supported: set[str] = set()

        for raw_symbol in watchlist:
            if not isinstance(raw_symbol, str):
                raise ValueError("watchlist entries must be strings")
            normalized = normalize_ticker(raw_symbol)
            if normalized in snapshot.tickers:
                if normalized in seen_supported:
                    duplicates.append(normalized)
                else:
                    supported.append(normalized)
                    seen_supported.add(normalized)
                    ordered_sections.append(("supported", normalized, None, None))
                continue
            if normalized in snapshot.invalid_inputs:
                ambiguous.append(
                    (raw_symbol, normalized, snapshot.invalid_inputs[normalized])
                )
                ordered_sections.append(
                    (
                        "ambiguous",
                        raw_symbol,
                        normalized,
                        snapshot.invalid_inputs[normalized],
                    )
                )
                continue
            unsupported.append((raw_symbol, normalized))
            ordered_sections.append(("unsupported", raw_symbol, normalized, None))

        evaluations = {
            symbol: self._scorer.evaluate(
                symbol, snapshot.tickers[symbol], snapshot.as_of_dt
            )
            for symbol in supported
        }
        scored = [
            symbol
            for symbol in supported
            if evaluations[symbol].score_breakdown is not None
        ]
        scored.sort(
            key=lambda symbol: (
                -evaluations[symbol].score_breakdown.total,
                supported.index(symbol),
            )  # type: ignore[union-attr]
        )
        unscored = [
            symbol
            for symbol in supported
            if evaluations[symbol].score_breakdown is None
        ]
        ranked_symbols = scored + unscored

        sections = [
            f"# Entry-Zone Strategy ({snapshot.as_of})",
            self._renderer.render_method_summary(),
            self._renderer.render_watchlist_summary(
                watchlist,
                supported,
                duplicates,
                ambiguous,
                unsupported,
                evaluations,
            ),
            self._renderer.render_comparison_table(
                ranked_symbols,
                supported,
                evaluations,
            ),
        ]

        for section_type, first, second, third in ordered_sections:
            if section_type == "supported":
                sections.append(
                    self._renderer.render_supported_ticker(
                        first,
                        snapshot.tickers[first],
                        snapshot.as_of_dt,
                        evaluations[first],
                    )
                )
            elif section_type == "ambiguous":
                assert second is not None and third is not None
                sections.append(
                    self._renderer.render_ambiguous_section(first, second, third)
                )
            else:
                assert second is not None
                sections.append(
                    self._renderer.render_unsupported_section(first, second)
                )

        sections.append(self._renderer.render_limitations())
        report = "\n\n".join(sections).strip() + "\n"
        self._renderer.assert_language(report)
        return report
