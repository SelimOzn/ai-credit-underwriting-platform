from app.models.application import LoanApplication
from app.tools.financial import (
    calculate_dti,
    calculate_lti,
    calculate_risk_score
)

app = LoanApplication(
    full_name="Ahmet Yılmaz",
    monthly_income=50000,
    requested_loan=250000,
    employment_years=2,
    existing_debt=100000,
    credit_score=710
)

dti = calculate_dti(app)
lti = calculate_lti(app)
risk = calculate_risk_score(
    app.credit_score,
    dti,
    app.employment_years
)

print("DTI:", dti)
print("LTI:", lti)
print("Risk:", risk)