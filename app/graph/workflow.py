from langgraph.graph import StateGraph, END
from app.models.state import AgentState
from app.agents import(
    data_collector,
    financial_analyst,
    risk_analyst,
    supervisor
)

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("data_collector", data_collector.run)
    graph.add_node("risk_analyst", risk_analyst.run)
    graph.add_node("supervisor", supervisor.run)
    graph.add_node("financial_analyst", financial_analyst.run)

    graph.set_entry_point("data_collector")

    graph.add_edge("data_collector", "financial_analyst")
    graph.add_edge("financial_analyst", "risk_analyst")
    graph.add_edge("risk_analyst", "supervisor")
    graph.add_edge("supervisor", END)

    return graph.compile()