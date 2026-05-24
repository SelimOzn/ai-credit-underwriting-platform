from app.rag.retreiver import search_policy
from app.models.state import AgentState
from app.models.outputs import PolicyDecisionOutput
from langchain_ollama import ChatOllama
import os

ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")

llm = ChatOllama(
    model="qwen2.5:7b",
    base_url=ollama_base_url,
    temperature=0
)


async def run(state: AgentState) -> AgentState:
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

    semantic_query_response = await llm.ainvoke(query_generator_prompt)
    semantic_query = semantic_query_response.content.strip()

    docs = search_policy(semantic_query)
    context = "\n\n---\n\n".join(docs)

    final_prompt = f"""
    You are a strict lending policy compliance officer.

    Applicant Data:
    - Credit Score: {app.credit_score}
    - Employment Years: {app.employment_years}
    - Debt-to-Income (DTI) Ratio: {state.debt_to_income_ratio}
    - Requested Loan: {app.requested_loan}

    Retrieved Policy Rules:
    {context}

    INSTRUCTIONS:
    1. Evaluate the applicant data based ONLY on the retrieved policy rules above.
    2. For your "recommendation", you MUST choose exactly ONE of the following keywords:
       - APPROVE (If all data complies with the rules for automatic approval)
       - REJECT (If the data hits a strict rejection rule)
       - MANUAL_REVIEW (If the rules specify a manual review is needed)
       - SUPERVISOR (If the rules specify supervisor approval is needed)
    3. For your "reason", briefly quote the specific rule that led to your decision.
    """

    structured_llm = llm.with_structured_output(PolicyDecisionOutput)
    result = await structured_llm.ainvoke(final_prompt)

    state.logs.append(f"Generated Semantic Query: {semantic_query}")
    state.logs.append("Policy docs retrieved and evaluated")

    state.policy_flags.append(f"recommendation: {result.recommendation}, reason: {result.reason}")

    return state