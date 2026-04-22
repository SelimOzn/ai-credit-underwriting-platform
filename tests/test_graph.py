from app.models.application import LoanApplication
from app.models.state import AgentState
from app.graph.workflow import build_graph

application = LoanApplication(
    full_name="Ahmet Yılmaz",
    monthly_income=300,
    requested_loan=250000,
    employment_years=0.3,
    existing_debt=1000000,
    credit_score=300
)

state = AgentState(application=application)

graph = build_graph()

result = graph.invoke(state)

print("Decision:", result["final_decision"])
print("Reasons:", result["reasons"])

print("Logs:")
for log in result["logs"]:
    print("-", log)