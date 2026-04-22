from app.models.state import AgentState

def run(state: AgentState) -> AgentState:
    explanation = f"""
Final Decision: {state.final_decision}

Risk Score: {state.risk_score}
DTI: {state.debt_to_income_ratio}
  
Reasons:
- {" | ".join(state.reasons)}
"""

    state.logs.append("Explainability Generated")
    state.policy_flags.append(explanation)

    return state