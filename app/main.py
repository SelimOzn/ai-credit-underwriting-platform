from fastapi import FastAPI, HTTPException
from app.models.application import LoanApplication
from app.models.decision import ManualDecision
from app.models.request import ReviewRequest
from app.graph.workflow import build_graph
from app.services.database import (get_all_applications,
                                   insert_application,
                                   get_application,
                                   get_pending_reviews,
                                   resolve_review,
                                   insert_audit)
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

        result = await loan_graph.ainvoke(initial_state)

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


@app.get("/pending-reviews")
async def get_pending_applications():
    try:
        rows = get_pending_reviews()
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pending Reviews Failed: {str(e)}")


@app.post("/resolve-review")
async def api_resolve_review(req: ReviewRequest):
    try:
        resolve_review(req.app_id, req.decision.value, req.reviewer, req.note)

        insert_audit(req.app_id, req.decision.value, req.reviewer, req.note)

        return {"status": "success", "app_id": req.app_id, "action_logged": req.decision.value}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Review Failed: {str(e)}")

@app.get("/applications")
async def api_get_applications():
    try:
        apps = get_all_applications()
        return apps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application List Failed: {str(e)}")

