from app.models.state import AgentState
from app.tools.financial import calculate_dti, calculate_lti

def run(state: AgentState) -> AgentState:
    state.debt_to_income_ratio = calculate_dti(state.application)
    lti = calculate_lti(state.application)

    state.logs.append(
        f"Financial Analyst: DTI={state.debt_to_income_ratio}, LTI={lti}"
    )

    return state