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
