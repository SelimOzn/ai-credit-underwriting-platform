import streamlit as st
from requests_toolbelt.multipart.encoder import total_len
import pandas as pd

from app.models.application import LoanApplication
from app.models.state import AgentState
from app.graph.workflow import build_graph
from app.services.database import (
    init_db,
    insert_application,
    get_all_applications,
    get_pending_reviews,
    resolve_review,
    init_audit_table,
    insert_audit
)

init_db()
init_audit_table()

st.set_page_config(
    page_title="AI Credit Underwriting Platform",
    layout="wide",
)


st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["New Application", "History Dashboard", "Human Review Queue", "Executive Dashboard"]
)

if page == "History Dashboard":
    rows = get_all_applications()

    st.title("Application History")

    st.write("Total Applications:", len(rows))

    approve_count = sum(1 for r in rows if r[6] == "APPROVE")
    reject_count = sum(1 for r in rows if r[6] == "REJECT")

    st.write("Approved:", approve_count)
    st.write("Rejected:", reject_count)

    st.dataframe(rows)
    st.stop()

if page == "Human Review Queue":
    st.title("Human Review Queue")
    rows = get_pending_reviews()

    for row in rows:
        app_id = row[0]

        with st.expander(f"Case #{app_id} - {row[1]}"):
            st.write("Income: ", row[2])
            st.write("Requested Loan: ", row[3])
            st.write("Credit Score: ", row[4])
            st.write("Risk Score: ", row[5])

            reviewer = st.text_input(f"Reviewer {app_id}", key=f"rev_{app_id}")
            note = st.text_input(f"Note {app_id}", key=f"note_{app_id}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Approve", key=f"a_{app_id}"):
                    resolve_review(app_id, "APPROVE", reviewer, note)
                    insert_audit(app_id, "MANUAL_DECISION_APPROVED", reviewer, note)
                    st.rerun()

            with col2:
                if st.button("Reject", key=f"r_{app_id}"):
                    resolve_review(app_id, "REJECT", reviewer, note)
                    insert_audit(app_id, "MANUAL_DECISION_REJECTED", reviewer, note)
                    st.rerun()
    st.stop()


if page == "Executive Dashboard":
    rows = get_all_applications()

    total = len(rows)

    approve = sum(1 for r in rows if r[6] == "APPROVE")
    reject = sum(1 for r in rows if r[6] == "REJECT")
    review = sum(1 for r in rows if r[6] == "MANUAL_REVIEW")

    st.title("Executive Dashboard")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total", total)
    c2.metric("Approved", approve)
    c3.metric("Rejected", reject)
    c4.metric("Manual Review", review)

    print(rows[1])
    df = pd.DataFrame(rows, columns=[
        "id", "name", "income", "loan",
        "credit", "risk", "decision", "created_at",
        "review_status", "reviewed_by", "review_note"
    ])

    st.subheader("Risk Score Distribution")
    st.bar_chart(df["risk"])
    st.write("Approval Rate:", round(approve / total * 100, 2), "%")
    st.stop()

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


    insert_application(
        full_name=full_name,
        monthly_income=monthly_income,
        requested_loan=requested_loan,
        credit_score=credit_score,
        risk_score=result["risk_score"],
        decision=result["final_decision"]
    )

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