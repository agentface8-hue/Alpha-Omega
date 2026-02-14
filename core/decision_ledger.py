"""
Decision Ledger: SQLite-backed storage of every recommendation.

Every decision is auditable:
- Inputs, agent votes, risk metrics, timestamps
- Future: outcome tracking at 7/30/90 day intervals
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from config.settings import settings


DB_PATH = os.path.join(settings.DATA_DIR, "decision_ledger.db")


def _ensure_db():
    """Create the database and tables if they don't exist. Migrate regime column if missing."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            recommendation TEXT,
            confidence REAL,
            confidence_breakdown TEXT,
            decision_matrix TEXT,
            agent_votes TEXT,
            risk_assessment TEXT,
            consensus_view TEXT,
            position_size_pct REAL,
            vetoed INTEGER DEFAULT 0,
            veto_reason TEXT,
            regime TEXT,
            outcome_7d REAL,
            outcome_30d REAL,
            outcome_90d REAL
        )
    """)
    # Migration: add regime column if it does not exist (existing DBs)
    cursor.execute("PRAGMA table_info(decisions)")
    columns = [row[1] for row in cursor.fetchall()]
    if "regime" not in columns:
        cursor.execute("ALTER TABLE decisions ADD COLUMN regime TEXT DEFAULT ''")
    conn.commit()
    conn.close()


def record_decision(decision_data: Dict[str, Any]) -> int:
    """Record a decision to the ledger. Returns the decision ID."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO decisions (
            timestamp, symbol, recommendation, confidence,
            confidence_breakdown, decision_matrix, agent_votes,
            risk_assessment, consensus_view, position_size_pct,
            vetoed, veto_reason, regime
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        decision_data.get("symbol", ""),
        decision_data.get("recommendation", ""),
        decision_data.get("confidence", 0.0),
        json.dumps(decision_data.get("confidence_breakdown", {})),
        json.dumps(decision_data.get("decision_matrix", {})),
        json.dumps(decision_data.get("agent_votes", {})),
        json.dumps(decision_data.get("risk_assessment", {})),
        decision_data.get("consensus_view", ""),
        decision_data.get("position_size_pct", 0.0),
        1 if decision_data.get("vetoed", False) else 0,
        decision_data.get("veto_reason", ""),
        decision_data.get("regime", ""),
    ))
    
    decision_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return decision_id


def get_recent_decisions(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve the most recent decisions."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM decisions ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        entry = dict(row)
        # Parse JSON fields
        for field in ['confidence_breakdown', 'decision_matrix', 'agent_votes', 'risk_assessment']:
            try:
                entry[field] = json.loads(entry[field]) if entry[field] else {}
            except (json.JSONDecodeError, TypeError):
                entry[field] = {}
        entry['vetoed'] = bool(entry.get('vetoed', 0))
        results.append(entry)
    
    return results


def get_decision_by_id(decision_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a specific decision by ID."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    entry = dict(row)
    for field in ['confidence_breakdown', 'decision_matrix', 'agent_votes', 'risk_assessment']:
        try:
            entry[field] = json.loads(entry[field]) if entry[field] else {}
        except (json.JSONDecodeError, TypeError):
            entry[field] = {}
    entry['vetoed'] = bool(entry.get('vetoed', 0))
    return entry


def update_decision_outcomes(
    decision_id: int,
    outcome_7d: Optional[float] = None,
    outcome_30d: Optional[float] = None,
    outcome_90d: Optional[float] = None,
) -> bool:
    """Update realized return outcomes for a decision. Returns True if row was updated."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    updates = []
    params = []
    if outcome_7d is not None:
        updates.append("outcome_7d = ?")
        params.append(outcome_7d)
    if outcome_30d is not None:
        updates.append("outcome_30d = ?")
        params.append(outcome_30d)
    if outcome_90d is not None:
        updates.append("outcome_90d = ?")
        params.append(outcome_90d)
    if not updates:
        conn.close()
        return False
    params.append(decision_id)
    cursor.execute(
        f"UPDATE decisions SET {', '.join(updates)} WHERE id = ?",
        params,
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def get_decisions_pending_outcomes(horizon_days: int, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Return decisions older than horizon_days that are missing the corresponding outcome.
    Used by the attribution evaluation job.
    """
    _ensure_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    col = f"outcome_{horizon_days}d"
    cursor.execute(
        f"""
        SELECT * FROM decisions
        WHERE {col} IS NULL
        AND datetime(timestamp) <= datetime('now', ?)
        ORDER BY timestamp ASC
        LIMIT ?
        """,
        (f"-{horizon_days} days", limit),
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for row in rows:
        entry = dict(row)
        for field in ['confidence_breakdown', 'decision_matrix', 'agent_votes', 'risk_assessment']:
            try:
                entry[field] = json.loads(entry[field]) if entry[field] else {}
            except (json.JSONDecodeError, TypeError):
                entry[field] = {}
        entry['vetoed'] = bool(entry.get('vetoed', 0))
        results.append(entry)
    return results
