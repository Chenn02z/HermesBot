"""Public facade for deterministic markdown generation for spec 0002."""

from __future__ import annotations

from hermes_finance._strategy_pipeline import EntryZoneStrategyPipeline


def generate_entry_zone_strategy(
    watchlist: list[str], as_of: str, fixture: dict
) -> str:
    """Return a deterministic markdown entry-zone strategy report."""
    return EntryZoneStrategyPipeline().generate(watchlist, as_of, fixture)
