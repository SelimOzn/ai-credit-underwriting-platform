from pydantic import BaseModel, Field

class LoanApplication(BaseModel):
    full_name: str = Field(..., min_length=3)
    monthly_income: float = Field(..., gt=0)
    requested_loan : float = Field(..., gt=0)
    employment_years: float = Field(..., ge=0)
    existing_debt: float = Field(..., ge=0)
    credit_score: int = Field(..., ge=300, le=850)