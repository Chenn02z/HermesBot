from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from hermes_finance._brief_utils import (
    QUOTE_FRESHNESS_WINDOW,
    freshness_status,
    parse_iso_datetime,
)

STRATEGY_FRESHNESS_WINDOW_DAYS = 7


@dataclass(frozen=True)
class ScoreBreakdown:
    trend_quality: int
    pullback_location_quality: int
    momentum_quality: int
    volume_quality: int
    volatility_quality: int

    @property
    def total(self) -> int:
        return (
            self.trend_quality
            + self.pullback_location_quality
            + self.momentum_quality
            + self.volume_quality
            + self.volatility_quality
        )


@dataclass(frozen=True)
class ObservationZone:
    evaluated: bool
    reason: str | None = None
    lower: float | None = None
    upper: float | None = None


@dataclass(frozen=True)
class StrategyEvaluation:
    symbol: str
    company_name: str | None
    quote_status: str
    strategy_statuses: Mapping[str, str]
    score_breakdown: ScoreBreakdown | None
    label: str
    insufficient_reasons: tuple[str, ...]
    conflict_notes: tuple[str, ...]
    observation_zone: ObservationZone


def strategy_freshness_status(timestamp: object, as_of_dt: datetime) -> str:
    if timestamp is None:
        return "stale"
    parsed = parse_iso_datetime(str(timestamp), "timestamp")
    if parsed > as_of_dt:
        return "invalid_future"
    age_days = (as_of_dt.date() - parsed.date()).days
    if age_days <= STRATEGY_FRESHNESS_WINDOW_DAYS:
        return "fresh"
    return "stale"


class StrategyScorer:
    def evaluate(
        self,
        symbol: str,
        payload: Mapping[str, object],
        as_of_dt: datetime,
    ) -> StrategyEvaluation:
        company_name = payload.get("company_name")
        company = (
            company_name
            if isinstance(company_name, str) and company_name.strip()
            else None
        )

        quote = payload.get("quote")
        strategy = payload.get("strategy")

        quote_status = self._quote_status(quote, as_of_dt)
        strategy_statuses = {
            "moving_averages": self._group_status(
                strategy, "moving_averages", as_of_dt
            ),
            "momentum": self._group_status(strategy, "momentum", as_of_dt),
            "range_52w": self._group_status(strategy, "range_52w", as_of_dt),
            "support_resistance": self._group_status(
                strategy, "support_resistance", as_of_dt
            ),
            "volatility": self._group_status(strategy, "volatility", as_of_dt),
            "volume": self._group_status(strategy, "volume", as_of_dt),
        }

        insufficient_reasons = self._insufficient_reasons(
            quote_status, strategy_statuses
        )
        breakdown = None if insufficient_reasons else self._score_breakdown(payload)
        label = (
            "Insufficient fresh evidence"
            if breakdown is None
            else self._label_for_score(breakdown.total)
        )
        conflict_notes = self._conflict_notes(payload)
        observation_zone = self._observation_zone(
            payload,
            quote_status,
            strategy_statuses,
            insufficient_reasons,
        )

        return StrategyEvaluation(
            symbol=symbol,
            company_name=company,
            quote_status=quote_status,
            strategy_statuses=strategy_statuses,
            score_breakdown=breakdown,
            label=label,
            insufficient_reasons=tuple(insufficient_reasons),
            conflict_notes=tuple(conflict_notes),
            observation_zone=observation_zone,
        )

    def _quote_status(self, quote: object, as_of_dt: datetime) -> str:
        if not isinstance(quote, Mapping):
            return "unavailable"
        return freshness_status(
            quote.get("timestamp"), as_of_dt, QUOTE_FRESHNESS_WINDOW
        )

    def _group_status(
        self, strategy: object, group_name: str, as_of_dt: datetime
    ) -> str:
        if not isinstance(strategy, Mapping):
            return "unavailable"
        group = strategy.get(group_name)
        if not isinstance(group, Mapping):
            return "unavailable"
        return strategy_freshness_status(group.get("timestamp"), as_of_dt)

    def _insufficient_reasons(
        self, quote_status: str, strategy_statuses: Mapping[str, str]
    ) -> list[str]:
        reasons: list[str] = []
        if quote_status != "fresh":
            reasons.append(f"quote evidence is {quote_status}")
        for group_name, status in strategy_statuses.items():
            if status != "fresh":
                reasons.append(f"strategy.{group_name} evidence is {status}")
        return reasons

    def _score_breakdown(self, payload: Mapping[str, object]) -> ScoreBreakdown:
        quote = payload["quote"]
        strategy = payload["strategy"]
        assert isinstance(quote, Mapping)
        assert isinstance(strategy, Mapping)

        moving_averages = strategy["moving_averages"]
        momentum = strategy["momentum"]
        range_52w = strategy["range_52w"]
        support_resistance = strategy["support_resistance"]
        volatility = strategy["volatility"]
        volume = strategy["volume"]
        assert isinstance(moving_averages, Mapping)
        assert isinstance(momentum, Mapping)
        assert isinstance(range_52w, Mapping)
        assert isinstance(support_resistance, Mapping)
        assert isinstance(volatility, Mapping)
        assert isinstance(volume, Mapping)

        current_price = float(quote["current_price"])
        sma_50 = float(moving_averages["sma_50"])
        sma_200 = float(moving_averages["sma_200"])
        support_1 = float(support_resistance["support_1"])
        resistance_1 = float(support_resistance["resistance_1"])
        range_high = float(range_52w["high"])
        rsi_14 = float(momentum["rsi_14"])
        atr_14 = float(volatility["atr_14"])
        latest_volume = float(volume["latest_volume"])
        avg_volume_20d = float(volume["avg_volume_20d"])

        trend = 0
        if current_price > sma_200:
            trend += 10
        if sma_50 > sma_200:
            trend += 10
        if current_price >= sma_50:
            trend += 5
        elif (sma_50 - current_price) / sma_50 <= 0.05:
            trend += 3

        pullback = 0
        support_distance = (current_price - support_1) / support_1
        if 0 <= support_distance <= 0.05:
            pullback += 12
        elif 0.05 < support_distance <= 0.10:
            pullback += 8
        elif 0.10 < support_distance <= 0.15:
            pullback += 4

        high_distance = (range_high - current_price) / range_high
        if 0.05 <= high_distance <= 0.25:
            pullback += 8
        elif 0 <= high_distance < 0.05:
            pullback += 4

        resistance_buffer = (resistance_1 - current_price) / current_price
        if resistance_buffer >= 0.08:
            pullback += 5
        elif 0.03 <= resistance_buffer < 0.08:
            pullback += 3

        momentum_points = 4
        if 40 <= rsi_14 <= 60:
            momentum_points = 20
        elif 30 <= rsi_14 < 40 or 60 < rsi_14 <= 70:
            momentum_points = 12

        volume_points = 0
        volume_ratio = latest_volume / avg_volume_20d
        if 0.8 <= volume_ratio <= 1.5:
            volume_points += 8
        elif 0.5 <= volume_ratio < 0.8 or 1.5 < volume_ratio <= 2.5:
            volume_points += 5

        if avg_volume_20d >= 1_000_000:
            volume_points += 7
        elif 250_000 <= avg_volume_20d < 1_000_000:
            volume_points += 4

        volatility_points = 3
        atr_ratio = atr_14 / current_price
        if 0.01 <= atr_ratio <= 0.04:
            volatility_points = 15
        elif atr_ratio < 0.01:
            volatility_points = 10
        elif 0.04 < atr_ratio <= 0.06:
            volatility_points = 8

        return ScoreBreakdown(
            trend_quality=trend,
            pullback_location_quality=pullback,
            momentum_quality=momentum_points,
            volume_quality=volume_points,
            volatility_quality=volatility_points,
        )

    def _label_for_score(self, score: int) -> str:
        if score >= 75:
            return "High-scoring research candidate"
        if score >= 60:
            return "Constructive research candidate"
        if score >= 45:
            return "Mixed research candidate"
        return "Weak research candidate"

    def _conflict_notes(self, payload: Mapping[str, object]) -> list[str]:
        notes: list[str] = []
        quote = payload.get("quote")
        strategy = payload.get("strategy")
        if not isinstance(quote, Mapping) or not isinstance(strategy, Mapping):
            return notes

        moving_averages = strategy.get("moving_averages")
        momentum = strategy.get("momentum")
        range_52w = strategy.get("range_52w")
        support_resistance = strategy.get("support_resistance")
        volatility = strategy.get("volatility")
        volume = strategy.get("volume")

        current_price = self._read_float(quote, "current_price")
        sma_50 = self._read_float(moving_averages, "sma_50")
        sma_200 = self._read_float(moving_averages, "sma_200")
        range_low = self._read_float(range_52w, "low")
        range_high = self._read_float(range_52w, "high")
        support_1 = self._read_float(support_resistance, "support_1")
        resistance_1 = self._read_float(support_resistance, "resistance_1")
        rsi_14 = self._read_float(momentum, "rsi_14")
        atr_14 = self._read_float(volatility, "atr_14")
        latest_volume = self._read_float(volume, "latest_volume")
        avg_volume_20d = self._read_float(volume, "avg_volume_20d")

        if sma_50 is not None and sma_200 is not None and sma_50 <= sma_200:
            notes.append(
                "50-day moving average is at or below the 200-day moving average."
            )
        if (
            current_price is not None
            and sma_200 is not None
            and current_price < sma_200
        ):
            notes.append("Current price is below the 200-day moving average.")
        if current_price is not None and sma_50 is not None and current_price < sma_50:
            notes.append("Current price is below the 50-day moving average.")
        if (
            current_price is not None
            and range_low is not None
            and range_high is not None
            and (current_price < range_low or current_price > range_high)
        ):
            notes.append("Current price sits outside the supplied 52-week range.")
        if (
            support_1 is not None
            and resistance_1 is not None
            and support_1 >= resistance_1
        ):
            notes.append("Support is at or above resistance in the supplied fixture.")
        if (
            current_price is not None
            and support_1 is not None
            and support_1 >= current_price
        ):
            notes.append("Support is at or above the current price.")
        if (
            current_price is not None
            and resistance_1 is not None
            and resistance_1 <= current_price
        ):
            notes.append("Resistance is at or below the current price.")
        if rsi_14 is not None and (rsi_14 < 30 or rsi_14 > 70):
            notes.append("RSI sits outside the 30 to 70 range.")
        if latest_volume is not None and avg_volume_20d is not None:
            volume_ratio = latest_volume / avg_volume_20d
            if volume_ratio < 0.5 or volume_ratio > 2.5:
                notes.append("Volume ratio is outside the 0.5 to 2.5 range.")
        if (
            current_price is not None
            and atr_14 is not None
            and atr_14 / current_price > 0.06
        ):
            notes.append("ATR ratio is above 0.06.")
        return notes

    def _observation_zone(
        self,
        payload: Mapping[str, object],
        quote_status: str,
        strategy_statuses: Mapping[str, str],
        insufficient_reasons: list[str],
    ) -> ObservationZone:
        if insufficient_reasons:
            return ObservationZone(
                evaluated=False,
                reason=insufficient_reasons[0],
            )
        if quote_status != "fresh":
            return ObservationZone(
                evaluated=False,
                reason=f"quote evidence is {quote_status}",
            )
        support_status = strategy_statuses["support_resistance"]
        if support_status != "fresh":
            return ObservationZone(
                evaluated=False,
                reason=f"strategy.support_resistance evidence is {support_status}",
            )
        volatility_status = strategy_statuses["volatility"]
        if volatility_status != "fresh":
            return ObservationZone(
                evaluated=False,
                reason=f"strategy.volatility evidence is {volatility_status}",
            )

        quote = payload["quote"]
        strategy = payload["strategy"]
        assert isinstance(quote, Mapping)
        assert isinstance(strategy, Mapping)
        support_resistance = strategy["support_resistance"]
        volatility = strategy["volatility"]
        assert isinstance(support_resistance, Mapping)
        assert isinstance(volatility, Mapping)

        current_price = float(quote["current_price"])
        support_1 = float(support_resistance["support_1"])
        resistance_1 = float(support_resistance["resistance_1"])
        atr_14 = float(volatility["atr_14"])

        if support_1 >= current_price:
            return ObservationZone(
                evaluated=False,
                reason="support is at or above the current price",
            )
        if support_1 >= resistance_1:
            return ObservationZone(
                evaluated=False,
                reason="support is at or above resistance",
            )

        lower = round(support_1, 2)
        upper = round(min(support_1 * 1.05, support_1 + 1.5 * atr_14), 2)
        if upper >= current_price:
            return ObservationZone(
                evaluated=False,
                reason="current price is already inside or below the observation zone",
            )

        return ObservationZone(evaluated=True, lower=lower, upper=upper)

    def _read_float(self, mapping: object, field: str) -> float | None:
        if not isinstance(mapping, Mapping):
            return None
        value = mapping.get(field)
        if value is None:
            return None
        return float(value)
