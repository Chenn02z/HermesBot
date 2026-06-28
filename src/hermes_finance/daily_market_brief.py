"""Public facade for deterministic markdown generation for spec 0001."""

from __future__ import annotations

from hermes_finance._brief_pipeline import BriefPipeline


def generate_daily_market_brief(
    watchlist: list[str], as_of: str, fixture: dict
) -> str:
    """Return a deterministic markdown finance brief."""
    return BriefPipeline().generate(watchlist, as_of, fixture)
