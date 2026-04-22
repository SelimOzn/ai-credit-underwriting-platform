from app.models.state import AgentState

def run(state: AgentState) -> AgentState:
    risk = state.risk_score
    dti = state.debt_to_income_ratio

    prompt = f"""
You are a credit policy analyst.

Application info:
- Risk Score: {risk}
- Debt To income Ratio: {dti}

Explain whether this case should:
1. be auto approved
2. go to manual review
3. be rejected

Keep explanation short and structured.
"""

    explanation = ""

    if risk > 0.7:
        explanation = "High risk detected → manual review recommended."
    elif dti > 0.8:
        explanation = "Debt burden too high → rejection risk."
    else:
        explanation = "Acceptable risk profile."

    state.policy_flags.append(explanation)
    state.logs.append(f"Policy Agent: {explanation}")

    return state