from fastapi import FastAPI, HTTPException
from app.models.application import LoanApplication
from app.graph.workflow import build_graph
from app.services.database import get_all_applications, insert_application, get_application
import uuid

app = FastAPI(title="Agentic Loan Evaluation API", version="1.0.0")

loan_graph = build_graph()

@app.get("/")
def read_root():
    return {"message": "Loan Evaluation API is running"}

@app.post("/evaluate")
async def evaluate_loan(application: LoanApplication):
    try:
        app_id = str(uuid.uuid4())

        initial_state = {
            "application": application,
            "app_id": app_id,
            "logs": [],
            "risk_score": 0.0,
            "is_approved": False
        }

        result = loan_graph.invoke(initial_state)

        insert_application(
            full_name=application.full_name,
            monthly_income=application.monthly_income,
            requested_loan=application.requested_loan,
            credit_score=application.credit_score,
            risk_score=result.get("risk_score"),
            decision=result.get("final_decision"),
        )

        return {
            "status":"success",
            "application_id": app_id,
            "decision": result.get("final_decision"),
            "logs": result.get("logs"),
            "risk_score": result.get("risk_score"),
            "debt_to_income_ratio": result.get("debt_to_income_ratio")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation Failed: {str(e)}")

@app.get("/status/{app_id}")
async def check_status(app_id: str):
    data = get_application(app_id)
    if not data:
        raise HTTPException(status_code=404, detail="Application not found")
    return data

