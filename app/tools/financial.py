from app.models.application import LoanApplication

def calculate_dti(application: LoanApplication) -> float:
    return round(
        application.existing_debt / application.monthly_income,
        4
    )

def calculate_lti(application: LoanApplication) -> float:
    return round(
        application.requested_loan / (12 * application.monthly_income),
        4
    )

def calculate_dti_tool(debt, income):
    return debt / income if income>0 else 999

def calculate_lti_tool(loan, income):
    return loan / income if income>0 else 999

def calculate_risk_score(
        credit_score:int,
        dti:float,
        employment_years:float,
        ) -> float:

    score = 0.0
    if credit_score < 550:
        score += 0.60
    elif credit_score < 650:
        score += 0.35
    else:
        score += 0.10

    if dti > 0.70:
        score += 0.30
    elif dti > 0.50:
        score += 0.20
    else:
        score += 0.05

    if employment_years<1:
        score += 0.25
    elif employment_years<3:
        score += 0.10
    else:
        score += 0.03

    return round(min(score, 1.0), 4)








