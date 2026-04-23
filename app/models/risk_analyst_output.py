from pydantic import BaseModel, Field

class RiskAnalystOutput(BaseModel):
    risk_score: float = Field(description="Risk score calculated between 0.0 and 1.0", ge=0.0, le=1.0)
    reason: str = Field(description="The short and clear reason for risk score calculation", min_length=1)
