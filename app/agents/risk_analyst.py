import json
import re

from app.models.state import AgentState
from app.llm.client import ask_llm
from app.tools.financial import calculate_dti_tool, calculate_lti_tool

def run(state: AgentState) -> AgentState:
    app = state.application

    planner_prompt = f"""
You are a credit risk agent.

Application:
income={app.monthly_income}
debt={app.existing_debt}
loan={app.requested_loan}

Available tools:
1. calculate_dti_tool
2. calculate_lti_tool

Return JSON only:

{{
 "tools":["calculate_dti_tool", "calculate_lti_tool"],
}}
"""

    raw = ask_llm(planner_prompt)
    match = re.search(r'\{.*\}', raw, re.S)

    if match:
        data = json.loads(match.group())
        tools = data.get("tools", [])
    else:
        tools = ["calculate_dti_tool", "calculate_lti_tool"]

    results = {}

    if "calculate_dti_tool" in tools:
        results["dti"] = calculate_dti_tool(
            app.existing_debt,
            app.monthly_income,
        )

    if "calculate_lti_tool" in tools:
        results["lti"] = calculate_lti_tool(
            app.requested_loan,
            app.monthly_income,
        )

    final_prompt = f"""
You are a senior underwriting analyst.

Application:
credit_score={app.credit_score}
employment_years={app.employment_years}

Tool results:
{results}

Return JSON only:

{{
"risk_score": 0.0,
"reason": "short explanation"
}}
"""

    raw2 = ask_llm(final_prompt)
    match2 = re.search(r'\{.*\}', raw2, re.S)

    if match2:
        output = json.loads(match2.group())

        risk = float(output["risk_score"])
        reason = output["reason"]
    else:
        risk = 0.50
        reason = "Fallback parsing used"

    state.risk_score = max(0, min(risk,1))
    state.reasons.append(reason)
    state.logs.append(f"Risk Agent tools used: {tools}")
    state.logs.append(f"Risk Agent result: {state.risk_score}")

    if "dti" in results:
        state.debt_to_income_ratio = results["dti"]

    return state

