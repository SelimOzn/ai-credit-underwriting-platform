from app.models.state import AgentState

async def run(state: AgentState) -> AgentState:
    state.logs.append("Data Collator: application received.")
    return state

