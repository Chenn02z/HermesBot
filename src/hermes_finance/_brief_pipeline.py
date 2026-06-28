from __future__ import annotations

from hermes_finance._brief_rendering import MarkdownRenderer
from hermes_finance._brief_utils import assert_report_language, normalize_ticker
from hermes_finance._brief_validation import EvidenceSnapshotValidator


class BriefPipeline:
    def __init__(
        self,
        validator: EvidenceSnapshotValidator | None = None,
        renderer: MarkdownRenderer | None = None,
    ) -> None:
        self._validator = validator or EvidenceSnapshotValidator()
        self._renderer = renderer or MarkdownRenderer()

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

        sections = [
            f"# Daily Market Brief ({snapshot.as_of})",
            self._renderer.render_market_context(
                snapshot.market_context,
                snapshot.as_of_dt,
                snapshot.market_context_complete,
            ),
            self._renderer.render_watchlist_summary(
                watchlist,
                supported,
                duplicates,
                ambiguous,
                unsupported,
            ),
        ]

        for section_type, first, second, third in ordered_sections:
            if section_type == "supported":
                sections.append(
                    self._renderer.render_supported_ticker(
                        first,
                        snapshot.tickers[first],
                        snapshot.as_of_dt,
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
        assert_report_language(report)
        return report
