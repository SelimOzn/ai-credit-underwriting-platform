from app.rag.retreiver import search_policy
from app.models.state import AgentState
from app.models.outputs import PolicyDecisionOutput
from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0
)


def run(state: AgentState) -> AgentState:
    app = state.application

    query_generator_prompt = f"""
    You are a search assistant. Your task is to generate a NATURAL LANGUAGE question for a vector-based document search engine (Semantic Search) using the provided customer data.

    Customer Data:
    credit_score={app.credit_score}
    employment_years={app.employment_years}
    DTI={state.debt_to_income_ratio}

    RULES:
    1. STRICTLY DO NOT use SQL (SELECT, WHERE, etc.) or any programming code.
    2. Write ONLY a plain, human-like question.
    3. Example of a correct output: "What are the minimum credit score and employment duration requirements for loan approval?"

    Return ONLY the generated question, with no additional explanations or conversational text.
    """

    semantic_query = llm.invoke(query_generator_prompt).content.strip()

    docs = search_policy(semantic_query)
    context = "\n\n---\n\n".join(docs)

    final_prompt = f"""
You are a lending policy compliance officer.

Applicant Data:
credit_score={app.credit_score}
employment_years={app.employment_years}
dti_ratio={state.debt_to_income_ratio}

Retrieved Policy Rules:
{context}

Based ONLY on the policy rules above, decide the outcome.
"""

    structured_llm = llm.with_structured_output(PolicyDecisionOutput)
    result = structured_llm.invoke(final_prompt)

    state.logs.append(f"Generated Semantic Query: {semantic_query}")
    state.logs.append("Policy docs retrieved and evaluated")

    state.policy_flags.append(f"recommendation: {result.recommendation}, reason: {result.reason}")

    return state