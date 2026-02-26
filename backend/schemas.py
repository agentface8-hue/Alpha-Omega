from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AnalysisRequest(BaseModel):
    symbol: str

class AgentLog(BaseModel):
    agent_name: str
    message: str
    timestamp: float

class AnalysisResponse(BaseModel):
    symbol: str
    consensus_view: str
    confidence_score: float
    executioner_decision: str
    full_report: Dict[str, Any]


class ScanRequest(BaseModel):
    symbols: List[str]

class ScanResponse(BaseModel):
    market_header: str = ""
    market_regime: str = ""
    vix_estimate: float = 0
    results: List[Dict[str, Any]] = []
    error: Optional[str] = None
