from app.models.state import AgentState
from app.models.risk_analyst_output import RiskAnalystOutput
from app.tools.registry import TOOL_REGISTRY
from app.tools.executor import execute_tool

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0
)

def run(state: AgentState) -> AgentState:
    app = state.application

    tools_list = list(TOOL_REGISTRY.values())
    llm_with_tools = llm.bind_tools(tools_list)

    messages = [
        SystemMessage(content="You are a credit risk agent. Use the tools provided to you to analyze customer status."),
        HumanMessage(content=f"Income: {app.monthly_income}, Debt: {app.existing_debt}, Loan: {app.requested_loan}")
    ]

    response = llm_with_tools.invoke(messages)
    tool_results = {}

    if hasattr(response, "tool_calls") and response.tool_calls:
        for tc in response.tool_calls:
            name = tc["name"]
            args = tc["args"]

            result = execute_tool(name, args)
            tool_results[name] = result

    final_prompt = f"""
You are a senior underwriting analyst.

IMPORTANT CALCULATION RULE:
The risk_score MUST be a probability float value strictly between 0.00 and 1.00.
- 0.00 means absolutely no risk.
- 0.50 means moderate risk.
- 1.00 means absolute maximum risk.
Do NOT use integer scales like 1, 2, or 3. Use decimals (e.g., 0.85).

Application:
credit_score={app.credit_score}
employment_years={app.employment_years}

Tool results:
{tool_results}
"""

    structured_llm = llm.with_structured_output(RiskAnalystOutput)
    final_result = structured_llm.invoke(final_prompt)

    state.risk_score = final_result.risk_score
    state.reasons.append(final_result.reason)

    state.logs.append(f"Tools used: {list(tool_results.keys())}")
    state.logs.append(f"Risk analyst output: {state.risk_score}")

    return state

