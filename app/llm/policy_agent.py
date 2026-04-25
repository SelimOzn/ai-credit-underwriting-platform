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
    You are an expert search query generator for a Semantic RAG system.
    Your task is to write a generalized, natural language search question to retrieve the relevant lending policy rules.

    Applicant Data:
    credit_score={app.credit_score}
    employment_years={app.employment_years}
    DTI={state.debt_to_income_ratio}

    CRITICAL RULES:
    1. DO NOT include the exact numbers (e.g., {app.credit_score}, {app.employment_years}) in your generated query. Policy documents contain general thresholds (e.g., "minimum score", "maximum DTI"), not exact applicant numbers.
    2. Ask a generalized question to find the *rules, limits, minimums, and maximums* governing these specific metrics.
    3. STRICTLY DO NOT use SQL or code.

    Example of a BAD query (Too specific): "Is a loan approved for a 710 credit score and 0 years of employment?"

    Return ONLY the generated question, with no additional conversational text.
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