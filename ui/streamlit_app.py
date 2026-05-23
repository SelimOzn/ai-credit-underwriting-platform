import streamlit as st
import requests
import pandas as pd
import os

BASE_API_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL = f"{BASE_API_URL}/evaluate"

from app.models.application import LoanApplication, LoanIntent, Ownership
from app.models.decision import Decision

st.set_page_config(
    page_title="AI Credit Underwriting Platform",
    layout="wide",
)

def get_pending_reviews_from_api():
    try:
        response = requests.get(f"{BASE_API_URL}/pending-reviews")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error getting pending reviews: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return []

def resolve_review_via_api(app_id, decision: Decision, reviewer: str, note: str):
    payload = {
        "application_id": str(app_id),
        "human_decision": decision.value,
        "human_feedback": f"Reviewer: {reviewer} | Note: {note}",
    }
    try:
        response = requests.post(f"{BASE_API_URL}/resume", json=payload)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error resolving review: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return False

def get_all_applications_from_api():
    try:
        response = requests.get(f"{BASE_API_URL}/applications")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error getting applications: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Backend connection error: {e}")
        return []


st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["New Application", "History Dashboard", "Human Review Queue", "Executive Dashboard"]
)

if page == "History Dashboard":
    rows = get_all_applications_from_api()

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

    if st.button("🔄 Verileri Güncelle"):
        st.rerun()

    rows = get_pending_reviews_from_api()

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
                    is_success = resolve_review_via_api(app_id, Decision.MANUAL_APPROVE, reviewer, note)
                    if is_success:
                        st.success("Application Approved")
                        st.rerun()

            with col2:
                if st.button("Reject", key=f"r_{app_id}"):
                    is_success = resolve_review_via_api(app_id, Decision.MANUAL_REJECT, reviewer, note)
                    if is_success:
                        st.success("Application Rejected")
                        st.rerun()
    st.stop()


if page == "Executive Dashboard":
    rows = get_all_applications_from_api()

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
    if total > 0:
        st.write("Approval Rate:", round(approve / total * 100, 2), "%")
    else:
        st.write("Approval Rate: 0%")
    st.stop()

st.title("AI Credit Underwriting Multi-Agent Platform")
st.subheader("Loan Application Form")

with st.form("loan_form"):
    full_name = st.text_input("Full Name", "Ahmet Yılmaz")
    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Annual Income", 1.0, 50000.0)
        employment_years = st.number_input("Employment Years", 0.0, 3.0)
        person_age = st.number_input("Age", min_value=18, max_value=100, value=28, step=1)

    with col2:
        requested_loan = st.number_input("Requested Loan", 1.0, 250000.0)
        existing_debt = st.number_input("Existing Debt", 0.0, 10000.0)
        person_home_ownership = st.selectbox("Home Ownership", [member.value for member in Ownership])
        loan_intent = st.selectbox("Loan Intent", [member.value for member in LoanIntent])
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
        home_ownership=person_home_ownership,
        loan_intent=loan_intent,
        age=person_age,
    )

    with st.spinner("AI agents are reviewing the application... This process may take a few seconds."):
        try:
            # Pydantic modelini JSON formatına (dict) çeviriyoruz
            payload = application.model_dump()

            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                result = response.json()
                api_status = result.get("status")
                decision = result.get("decision", "UNKNOWN")

                st.markdown("---")
                st.subheader(f"Application result (ID: {result.get('application_id')})")

                # Sonuç ekranı
                if decision == "pending_human_review":
                    st.success("The AI has completed preliminary checks, but this application requires MANUAL REVIEW. Execution is paused.")
                elif decision == "REJECT":
                    st.error("Loan Application AUTO-REJECTED")
                elif decision == "APPROVE":
                    st.warning("Loan Application AUTO-APPROVED.")

                st.divider()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Decision", decision)
                with col2:
                    st.metric("Risk Score", result.get("risk_score", "N/A"))
                with col3:
                    st.metric("System Status", api_status.replace("_", " ").upper())

                with st.expander("View Agents' Decision-Making Process Logs", expanded=False):
                    for log in result.get("logs", []):
                        st.info(log)
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("""The backend service is unreachable! 
            Please ensure the FastAPI server is running by using 
            the command `uvicorn app.main:app --reload` in a separate terminal.""")