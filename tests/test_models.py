from app.models.application import LoanApplication

app = LoanApplication(
    full_name="Ahmet Yılmaz",
    monthly_income=5000,
    requested_loan=25000,
    employment_years=2,
    existing_debt=100000,
    credit_score=8000,
)

print(app)