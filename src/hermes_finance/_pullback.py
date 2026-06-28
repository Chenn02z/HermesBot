from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from hermes_finance._brief_utils import QUOTE_FRESHNESS_WINDOW, freshness_status


@dataclass(frozen=True)
class PullbackResult:
    status: str
    reason: str | None = None
    lower: float | None = None
    upper: float | None = None
    reference_source: str | None = None
    reference_timestamp: object | None = None


class PullbackEvaluator:
    def evaluate(
        self,
        payload: Mapping[str, object],
        as_of_dt: datetime,
    ) -> PullbackResult:
        quote = payload.get("quote")
        if not isinstance(quote, Mapping):
            return PullbackResult(
                status="skipped",
                reason="quote evidence is unavailable",
            )

        range_data = payload.get("range_20d")
        if not isinstance(range_data, Mapping):
            return PullbackResult(
                status="skipped",
                reason="20-day range evidence is unavailable",
            )

        current_price = quote.get("current_price")
        recent_low = range_data.get("recent_low_20d")
        recent_high = range_data.get("recent_high_20d")
        if current_price is None or recent_low is None or recent_high is None:
            return PullbackResult(
                status="skipped",
                reason="required pullback fields are missing",
            )

        quote_status = freshness_status(
            quote.get("timestamp"),
            as_of_dt,
            QUOTE_FRESHNESS_WINDOW,
        )
        if quote_status != "fresh":
            return PullbackResult(
                status="skipped",
                reason=f"quote evidence is {quote_status}",
            )

        range_status = freshness_status(
            range_data.get("timestamp"),
            as_of_dt,
            QUOTE_FRESHNESS_WINDOW,
        )
        if range_status != "fresh":
            return PullbackResult(
                status="skipped",
                reason=f"20-day range evidence is {range_status}",
            )

        reference_price = float(recent_low)
        reference_source = "range_20d.recent_low_20d"
        reference_timestamp = range_data.get("timestamp")

        support_level = payload.get("support_level")
        if isinstance(support_level, Mapping):
            support_price = support_level.get("price")
            support_status = freshness_status(
                support_level.get("timestamp"),
                as_of_dt,
                QUOTE_FRESHNESS_WINDOW,
            )
            if support_price is not None and support_status == "fresh":
                reference_price = float(support_price)
                reference_source = "support_level.price"
                reference_timestamp = support_level.get("timestamp")

        lower = round(reference_price, 2)
        upper = round(reference_price * 1.03, 2)
        if upper >= float(current_price):
            return PullbackResult(
                status="skipped",
                reason="candidate zone upper bound is greater than or equal to "
                "current price",
            )

        return PullbackResult(
            status="evaluated",
            lower=lower,
            upper=upper,
            reference_source=reference_source,
            reference_timestamp=reference_timestamp,
        )
