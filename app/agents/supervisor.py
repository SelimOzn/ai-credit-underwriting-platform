from app.models.state import AgentState
from app.models.decision import Decision

async def run(state: AgentState) -> AgentState:
    app = state.application
    dti = state.debt_to_income_ratio
    risk = state.risk_score

    if app.credit_score < 550:
        state.final_decision = Decision.REJECT
        state.reasons.append("Very low credit score")

    elif dti > 1.0:
        state.final_decision = Decision.REJECT
        state.reasons.append("Debt too high")

    elif risk > 0.70:
        state.final_decision = Decision.MANUAL_REVIEW
        state.reasons.append("High risk requires review")

    else:
        state.final_decision = Decision.APPROVE
        state.reasons.append("Application acceptable")

    state.logs.append(
        f"Supervisor: final_decision={state.final_decision}"
    )

    return state