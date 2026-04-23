from pydantic import BaseModel, Field
from typing import Literal

class RiskAnalystOutput(BaseModel):
    risk_score: float = Field(description="Risk score calculated between 0.0 and 1.0", ge=0.0, le=1.0)
    reason: str = Field(description="The short and clear reason for risk score calculation", min_length=1)

class PolicyDecisionOutput(BaseModel):
    recommendation: Literal["APPROVE", "REJECT", "MANUAL_REVIEW"] = Field(
        description="The final decision based on policy")
    reason: str = Field(description="Short explanation based ONLY on the retrieved policy context")
