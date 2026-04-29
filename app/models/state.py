from pydantic import BaseModel
from typing import Optional, List
from .application import LoanApplication
from .decision import Decision

class AgentState(BaseModel):
    application : LoanApplication

    debt_to_income_ratio: Optional[float] = None
    risk_score: Optional[float] = None
    policy_flags: List[str] = []
    external_data: Optional[dict]
    final_decision: Optional[Decision] = None
    reasons: List[str] = []
    logs: List[str] = []