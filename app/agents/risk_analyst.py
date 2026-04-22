from app.models.state import AgentState
from app.tools.financial import calculate_risk_score

def run(state: AgentState) -> AgentState:
    state.risk_score = calculate_risk_score(
        state.application.credit_score,
        state.debt_to_income_ratio,
        state.application.employment_years
    )

    state.logs.append(
        f"Risk Analyst: risk_score={state.risk_score}"
    )

    return state
