import streamlit as st

from app.models.application import LoanApplication
from app.models.state import AgentState
from app.graph.workflow import build_graph

st.set_page_config(
    page_title="AI Credit Underwriting Platform",
    layout="wide",
)

st.title("AI Credit Underwriting Multi-Agent Platform")
st.subheader("Loan Application Form")

with st.form("loan_form"):
    full_name = st.text_input("Full Name", "Ahmet Yılmaz")
    monthly_income = st.number_input("Monthly Income", 1.0, 50000.0)
    requested_loan = st.number_input("Requested Loan", 1.0, 250000.0)
    employment_years = st.number_input("Employment Years", 0.0, 3.0)
    existing_debt = st.number_input("Existing Debt", 0.0, 10000.0)
    credit_score = st.slider("Credit Score", 300, 850, 710)

    submitted = st.form_submit_button("Evaluate Application")

if submitted:
    application = LoanApplication(
        full_name=full_name,
        monthly_income=monthly_income,
        requested_loan=requested_loan,
        employment_years=employment_years,
        existing_debt=existing_debt,
        credit_score=credit_score,
    )

    state = AgentState(application=application)

    graph = build_graph()
    result = graph.invoke(state)

    st.divider()


    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Decision", result["final_decision"])

    with col2:
        st.metric("Risk Score", result["risk_score"])

    with col3:
        st.metric("DTI", result["debt_to_income_ratio"])

    st.subheader("Reasons")

    for reason in result["reasons"]:
        st.write("-", reason)

    st.subheader("Agent Logs")

    for log in result["logs"]:
        st.code(log)

    st.subheader("Policy / Explainability")

    for item in result["policy_flags"]:
        st.info(item)