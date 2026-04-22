from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from app.models.decision import Decision
from app.agents import(
    data_collector,
    financial_analyst,
    risk_analyst,
    supervisor
)
from app.llm.policy_agent import run as policy_agent
from app.llm.explainability_agent import run as explain_agent


def route_by_risk(state: AgentState):
    risk = state.risk_score

    if risk is None:
        return "supervisor"
    elif risk < 0.3:
        return "auto_approve"
    elif risk < 0.7:
        return "supervisor"
    else:
        return "manual_review"


def auto_approve(state: AgentState):
    state.final_decision = Decision.APPROVE
    state.reasons.append("Auto-approved due to low risk")
    state.logs.append("Auto approval triggered")
    return state

def manual_review(state: AgentState):
    state.final_decision = Decision.MANUAL_REVIEW
    state.reasons.append("High risk requires human review")
    state.logs.append("Manual review triggered")
    return state


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("data_collector", data_collector.run)
    graph.add_node("risk_analyst", risk_analyst.run)
    graph.add_node("supervisor", supervisor.run)
    graph.add_node("financial_analyst", financial_analyst.run)
    graph.add_node("auto_approve", auto_approve)
    graph.add_node("manual_review", manual_review)
    graph.add_node("policy_agent", policy_agent)
    graph.add_node("explainability", explain_agent)

    graph.set_entry_point("data_collector")

    graph.add_edge("data_collector", "financial_analyst")
    graph.add_edge("financial_analyst", "risk_analyst")
    graph.add_edge("risk_analyst", "policy_agent")

    graph.add_conditional_edges(
        "policy_agent",
        route_by_risk,
        {
            "auto_approve":"auto_approve",
            "manual_review":"manual_review",
            "supervisor":"supervisor",
         }
    )

    graph.add_edge("auto_approve", END)
    graph.add_edge("manual_review", END)
    graph.add_edge("supervisor", "explainability")
    graph.add_edge("explainability", END)

    return graph.compile()