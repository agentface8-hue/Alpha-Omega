"""
Agent Performance Attribution.

Measures per-agent contribution to decision quality across:
- Directional (signal vs realized outcome)
- Risk (veto quality, drawdown prevention)
- Calibration (confidence vs correctness)
- Regime (segment by regime for future dynamic weighting)

Phase 1: Evaluate decisions at T+7/30/90, write AgentAttributionRecord.
Phase 2: Aggregation by agent/regime/horizon (observe only).

GUARDRAIL: Attribution is OBSERVE-ONLY. Attribution data must not affect
orchestrator behavior. Do not feed scores into agent weighting, UX, or
decisions until explicitly enabled after review. Prevents silent learning
bugs in finance.
"""
import sqlite3

# -----------------------------------------------------------------------------
# GUARDRAIL: Attribution must not affect decisions (observe-only mode).
# Changing this or feeding attribution into the orchestrator requires explicit
# review. Do not use attribution data for weighting, veto logic, or UX yet.
# -----------------------------------------------------------------------------
ATTRIBUTION_MODE = "observe_only"  # do not affect decisions
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from config.settings import settings

# Reuse same DB directory; separate table in same DB or same file for simplicity
DB_PATH = os.path.join(settings.DATA_DIR, "decision_ledger.db")

# Signal direction constants (must match agents.base_agent.SignalDirection values)
BUY_SIGNALS = ("STRONG_BUY", "BUY")
SELL_SIGNALS = ("STRONG_SELL", "SELL", "VETO")


@dataclass
class AgentAttributionRecord:
    """Per-agent, per-decision, per-horizon attribution record."""
    decision_id: int
    agent_name: str
    signal: str
    confidence: float
    veto: bool
    regime: str
    horizon: str  # "7d" | "30d" | "90d"
    realized_return: float
    max_drawdown: float
    directional_score: float = 0.0
    risk_score: float = 0.0
    calibration_score: float = 0.0
    total_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "agent_name": self.agent_name,
            "signal": self.signal,
            "confidence": round(self.confidence, 3),
            "veto": self.veto,
            "regime": self.regime,
            "horizon": self.horizon,
            "realized_return": round(self.realized_return, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "directional_score": round(self.directional_score, 4),
            "risk_score": round(self.risk_score, 4),
            "calibration_score": round(self.calibration_score, 4),
            "total_score": round(self.total_score, 4),
        }


def _ensure_attribution_table():
    """Create agent_attribution table if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_attribution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id INTEGER NOT NULL,
            agent_name TEXT NOT NULL,
            signal TEXT NOT NULL,
            confidence REAL NOT NULL,
            veto INTEGER NOT NULL,
            regime TEXT NOT NULL,
            horizon TEXT NOT NULL,
            realized_return REAL NOT NULL,
            max_drawdown REAL NOT NULL,
            directional_score REAL NOT NULL,
            risk_score REAL NOT NULL,
            calibration_score REAL NOT NULL,
            total_score REAL NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(decision_id, agent_name, horizon)
        )
    """)
    conn.commit()
    conn.close()


def _directional_score(signal: str, realized_return: float) -> float:
    """
    +1 if signal aligned with outcome, -1 if opposite. Magnitude-adjusted.
    Scale by min(|return|*10, 1) so bigger moves matter more.
    """
    magnitude = min(abs(realized_return) * 10.0, 1.0)
    if magnitude < 0.001:
        return 0.0
    correct = False
    if signal in BUY_SIGNALS and realized_return > 0:
        correct = True
    elif signal in SELL_SIGNALS and realized_return < 0:
        correct = True
    elif signal == "NEUTRAL":
        correct = True  # Neutral doesn't get penalized heavily
    return magnitude if correct else -magnitude


def _risk_score(
    veto: bool,
    recommendation: str,
    realized_return: float,
    position_size_pct: float,
) -> float:
    """
    Risk prevention beats profit generation.
    Correct veto (avoided loss) = high positive. Missed veto (loss taken) = negative.
    """
    traded = recommendation not in ("VETO", "NO_TRADE") and position_size_pct > 0
    if veto and not traded:
        # We vetoed (or veto drove no trade). If return was bad, we avoided loss.
        if realized_return < -0.01:
            return 1.0  # Correct veto
        if realized_return > 0.05:
            return -0.3  # Missed gain
        return 0.0
    if not veto and traded:
        if realized_return < -0.05:
            return -1.0  # Didn't prevent bad trade
        if realized_return > 0:
            return 0.5  # Good outcome
    return 0.0


def _calibration_score(confidence: float, correct: bool) -> float:
    """
    Penalize high confidence + wrong. Reward high confidence + right.
    Low confidence + wrong = smaller penalty.
    """
    if correct:
        return 0.2 + 0.3 * confidence  # [0.2, 0.5]
    return -0.2 - 0.3 * confidence  # [-0.5, -0.2]


def compute_realized_return(
    symbol: str,
    decision_timestamp: str,
    horizon_days: int,
) -> Tuple[float, float]:
    """
    Fetch prices at decision date and at T+horizon; return (realized_return, max_drawdown).
    max_drawdown is the worst peak-to-trough over the period (simplified: use min daily return if single period).
    """
    try:
        import yfinance as yf
    except ImportError:
        return 0.0, 0.0
    try:
        dt = datetime.fromisoformat(decision_timestamp.replace("Z", "+00:00"))
    except Exception:
        dt = datetime.utcnow() - timedelta(days=horizon_days)
    if dt.tzinfo:
        dt = dt.replace(tzinfo=None)
    start = (dt - timedelta(days=2)).strftime("%Y-%m-%d")
    end_dt = dt + timedelta(days=horizon_days + 2)
    end = end_dt.strftime("%Y-%m-%d")
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start, end=end, auto_adjust=True)
    if hist is None or hist.empty or len(hist) < 2:
        return 0.0, 0.0
    hist = hist.sort_index()
    # Price at decision (first date on or after decision)
    prices = hist["Close"]
    p0 = prices.iloc[0]
    # Price at T+horizon (last date in window or closest)
    if len(prices) < 2:
        return 0.0, 0.0
    p_end = prices.iloc[-1]
    realized = (p_end - p0) / p0 if p0 and p0 != 0 else 0.0
    # Max drawdown over period: min of (p - running_max) / running_max
    cummax = prices.cummax()
    drawdowns = (prices - cummax) / cummax.replace(0, float("nan"))
    max_dd = float(drawdowns.min()) if not drawdowns.empty else 0.0
    return realized, max_dd


def _get_regime_from_decision(decision: Dict[str, Any]) -> str:
    """Read regime from decision ledger (persisted at decision time). Do not infer from agent_votes."""
    return (decision.get("regime") or "UNKNOWN").strip() or "UNKNOWN"


def record_attribution(records: List[AgentAttributionRecord]) -> None:
    """Insert or replace attribution records for (decision_id, agent_name, horizon)."""
    _ensure_attribution_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    for r in records:
        cursor.execute(
            """
            INSERT OR REPLACE INTO agent_attribution (
                decision_id, agent_name, signal, confidence, veto, regime,
                horizon, realized_return, max_drawdown,
                directional_score, risk_score, calibration_score, total_score,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r.decision_id,
                r.agent_name,
                r.signal,
                r.confidence,
                1 if r.veto else 0,
                r.regime,
                r.horizon,
                r.realized_return,
                r.max_drawdown,
                r.directional_score,
                r.risk_score,
                r.calibration_score,
                r.total_score,
                now,
            ),
        )
    conn.commit()
    conn.close()


def evaluate_decision_for_horizon(
    decision: Dict[str, Any],
    horizon_days: int,
    realized_return: float,
    max_drawdown: float,
) -> List[AgentAttributionRecord]:
    """
    Compute per-agent scores for one decision at one horizon.
    Does not update decision outcomes; caller should call update_decision_outcomes.
    """
    decision_id = decision["id"]
    symbol = decision["symbol"]
    recommendation = (decision.get("recommendation") or "HOLD").upper()
    position_size_pct = float(decision.get("position_size_pct") or 0)
    vetoed = decision.get("vetoed", False)
    regime = _get_regime_from_decision(decision)
    horizon = f"{horizon_days}d"
    agent_votes = decision.get("agent_votes") or {}
    records = []
    for agent_name, vote in agent_votes.items():
        if not isinstance(vote, dict):
            continue
        signal = vote.get("signal", "NEUTRAL")
        confidence = float(vote.get("confidence", 0.5))
        veto = bool(vote.get("veto", False))
        directional_score = _directional_score(signal, realized_return)
        risk_score = _risk_score(veto, recommendation, realized_return, position_size_pct)
        correct = (signal in BUY_SIGNALS and realized_return > 0) or (
            signal in SELL_SIGNALS and realized_return < 0
        ) or (signal == "NEUTRAL")
        calibration_score = _calibration_score(confidence, correct)
        total_score = directional_score + risk_score * 1.5 + calibration_score
        records.append(
            AgentAttributionRecord(
                decision_id=decision_id,
                agent_name=agent_name,
                signal=signal,
                confidence=confidence,
                veto=veto,
                regime=regime,
                horizon=horizon,
                realized_return=realized_return,
                max_drawdown=max_drawdown,
                directional_score=directional_score,
                risk_score=risk_score,
                calibration_score=calibration_score,
                total_score=total_score,
            )
        )
    return records


def run_evaluation_job(horizon_days: int = 7, limit: int = 50) -> int:
    """
    Find decisions pending outcome for this horizon, compute realized return,
    update decision outcomes, write attribution records. Returns count of decisions evaluated.
    """
    from core.decision_ledger import get_decisions_pending_outcomes, update_decision_outcomes

    decisions = get_decisions_pending_outcomes(horizon_days, limit=limit)
    evaluated = 0
    for decision in decisions:
        symbol = decision.get("symbol", "")
        ts = decision.get("timestamp", "")
        if not symbol or not ts:
            continue
        realized_return, max_drawdown = compute_realized_return(symbol, ts, horizon_days)
        update_decision_outcomes(
            decision["id"],
            **{f"outcome_{horizon_days}d": realized_return},
        )
        records = evaluate_decision_for_horizon(
            decision, horizon_days, realized_return, max_drawdown
        )
        if records:
            record_attribution(records)
            evaluated += 1
    return evaluated


def run_full_evaluation_job(limit_per_horizon: int = 50) -> Dict[str, int]:
    """
    Run evaluation for 7d, 30d, and 90d horizons. Returns counts per horizon.
    """
    counts = {}
    for h in (7, 30, 90):
        counts[f"{h}d"] = run_evaluation_job(horizon_days=h, limit=limit_per_horizon)
    return counts


def get_attribution_by_decision(decision_id: int) -> List[Dict[str, Any]]:
    """Return all attribution records for a decision."""
    _ensure_attribution_table()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM agent_attribution WHERE decision_id = ? ORDER BY agent_name, horizon",
        (decision_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_aggregated_by_agent_regime_horizon(
    min_records: int = 1,
) -> List[Dict[str, Any]]:
    """
    Phase 2: Roll up total_score by agent, regime, horizon (rolling average).
    Returns list of { agent_name, regime, horizon, avg_total_score, record_count }.
    """
    _ensure_attribution_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT agent_name, regime, horizon,
               AVG(total_score) AS avg_total_score,
               COUNT(*) AS record_count
        FROM agent_attribution
        GROUP BY agent_name, regime, horizon
        HAVING COUNT(*) >= ?
        ORDER BY agent_name, regime, horizon
        """,
        (min_records,),
    )
    rows = cursor.fetchall()
    columns = [d[0] for d in cursor.description] if cursor.description else []
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def get_agent_summary(agent_name: str) -> Dict[str, Any]:
    """
    Summary for one agent: avg scores by horizon and by regime.
    """
    _ensure_attribution_table()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT horizon, regime,
               AVG(total_score) AS avg_total,
               AVG(directional_score) AS avg_directional,
               AVG(risk_score) AS avg_risk,
               AVG(calibration_score) AS avg_calibration,
               COUNT(*) AS n
        FROM agent_attribution
        WHERE agent_name = ?
        GROUP BY horizon, regime
        """,
        (agent_name,),
    )
    rows = cursor.fetchall()
    conn.close()
    by_horizon_regime = [dict(r) for r in rows]
    return {"agent_name": agent_name, "by_horizon_regime": by_horizon_regime}


if __name__ == "__main__":
    """Run full attribution evaluation (7d, 30d, 90d). Use as: python -m core.attribution"""
    counts = run_full_evaluation_job(limit_per_horizon=50)
    print("Attribution evaluation complete:", counts)
