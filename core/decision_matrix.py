"""
Decision Matrix: Replaces single BUY/SELL with multi-scenario analysis.

Instead of a binary decision, provides:
- Base / Bull / Bear scenarios with probabilities
- Expected returns and max drawdown per scenario
- Weighted expected return
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Scenario:
    """One scenario in the decision matrix."""
    name: str               # "Base", "Bull", "Bear"
    probability: float      # 0.0 to 1.0
    expected_return: float   # e.g. +0.12 for +12%
    max_drawdown: float      # e.g. -0.05 for -5%
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "probability": round(self.probability, 2),
            "expected_return": round(self.expected_return, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "description": self.description
        }


@dataclass
class DecisionMatrix:
    """
    Multi-scenario decision output replacing single BUY/SELL.
    
    Provides:
    - 3 scenarios (Base, Bull, Bear) with probabilities
    - Weighted expected return
    - Risk-adjusted recommendation
    """
    symbol: str
    scenarios: List[Scenario] = field(default_factory=list)
    recommendation: str = "HOLD"            # BUY / HOLD / SELL
    advisory_action: str = ""               # Detailed advisory text
    position_size_pct: float = 0.0          # Recommended allocation %
    stop_loss_pct: float = -5.0             # Default -5%
    target_pct: float = 10.0               # Default +10%
    risk_reward_ratio: float = 2.0

    @property
    def weighted_expected_return(self) -> float:
        """Probability-weighted expected return across all scenarios."""
        if not self.scenarios:
            return 0.0
        return sum(s.probability * s.expected_return for s in self.scenarios)

    @property
    def weighted_max_drawdown(self) -> float:
        """Worst-case weighted drawdown."""
        if not self.scenarios:
            return 0.0
        return min(s.max_drawdown for s in self.scenarios)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "recommendation": self.recommendation,
            "advisory_action": self.advisory_action,
            "position_size_pct": round(self.position_size_pct, 2),
            "stop_loss_pct": round(self.stop_loss_pct, 2),
            "target_pct": round(self.target_pct, 2),
            "risk_reward_ratio": round(self.risk_reward_ratio, 2),
            "weighted_expected_return": round(self.weighted_expected_return, 4),
            "weighted_max_drawdown": round(self.weighted_max_drawdown, 4),
            "scenarios": [s.to_dict() for s in self.scenarios],
        }


def build_default_scenarios(confidence: float, signal: str) -> List[Scenario]:
    """
    Generate default scenarios based on confidence and signal direction.
    Used when LLM cannot provide explicit scenario data.
    """
    is_bullish = signal in ("BUY", "STRONG_BUY")
    is_bearish = signal in ("SELL", "STRONG_SELL")
    
    if is_bullish:
        return [
            Scenario("Base", 0.55, confidence * 0.15, -0.05, "Consensus thesis plays out moderately."),
            Scenario("Bull", 0.25, confidence * 0.25, -0.03, "Catalysts trigger accelerated upside."),
            Scenario("Bear", 0.20, -0.08, -0.12, "Bear case materializes; thesis invalidated."),
        ]
    elif is_bearish:
        return [
            Scenario("Base", 0.50, -0.08, -0.10, "Bearish thesis confirmed, gradual decline."),
            Scenario("Bull", 0.20, 0.05, -0.04, "Unexpected positive catalyst reverses trend."),
            Scenario("Bear", 0.30, -0.15, -0.20, "Severe selloff beyond expectations."),
        ]
    else:
        return [
            Scenario("Base", 0.60, 0.02, -0.04, "Range-bound trading continues."),
            Scenario("Bull", 0.20, 0.10, -0.03, "Breakout above resistance."),
            Scenario("Bear", 0.20, -0.06, -0.10, "Breakdown below support."),
        ]
