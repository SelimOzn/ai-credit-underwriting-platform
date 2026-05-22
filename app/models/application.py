from pydantic import BaseModel, Field
from enum import Enum

class LoanIntent(str, Enum):
    EDUCATION = 'EDUCATION'
    MEDICAL = 'MEDICAL'
    VENTURE = 'VENTURE',
    PERSONAL = 'PERSONAL'
    IMPROVEMENT = 'HOMEIMPROVEMENT'
    CONSOLIDATION = 'DEBTCONSOLIDATION'

class Ownership(str, Enum):
    OWN = 'OWN',
    MORTGAGE = 'MORTGAGE'
    RENT = 'RENT'
    OTHER = 'OTHER'

class LoanApplication(BaseModel):
    full_name: str = Field(..., min_length=3)
    monthly_income: float = Field(..., gt=0)
    requested_loan : float = Field(..., gt=0)
    employment_years: float = Field(..., ge=0)
    existing_debt: float = Field(..., ge=0)
    credit_score: int = Field(..., ge=300, le=850)
    age: int = Field(..., ge=18, description="The applicant's age.")
    home_ownership: Ownership = Field(..., description="RENT, OWN, MORTGAGE etc.")
    loan_intent: LoanIntent = Field(..., description="EDUCATION, MEDICALVENTURE, PERSONAL, HOMEIMPROVEMENT, "
                                                     "DEBTCONSOLIDATION")