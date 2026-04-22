from app.models.application import LoanApplication
from app.models.state import AgentState

from app.agents import (
    data_collector,
    financial_analyst,
    risk_analyst,
    supervisor
)

application = LoanApplication(
    full_name="Ahmet Yılmaz",
    monthly_income=50000,
    requested_loan=250000,
    employment_years=3,
    existing_debt=10000,
    credit_score=710
)

state = AgentState(application=application)

state = data_collector.run(state)
state = financial_analyst.run(state)
state = risk_analyst.run(state)
state = supervisor.run(state)

print("Decision:", state.final_decision)
print("Reasons:", state.reasons)
print("Logs:")

for log in state.logs:
    print("-", log)