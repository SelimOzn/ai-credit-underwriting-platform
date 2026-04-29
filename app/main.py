import os

from fastapi import FastAPI, HTTPException
from app.models.application import LoanApplication
from app.models.request import ReviewRequest, HumanReviewRequest
from app.graph.workflow import build_graph
from app.services.database import (get_all_applications,
                                   insert_application,
                                   get_application,
                                   get_pending_reviews,
                                   resolve_review,
                                   insert_audit,
                                   init_db,
                                   init_audit_table)
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import uuid

app = FastAPI(title="Agentic Loan Evaluation API", version="1.0.0")


init_db()
init_audit_table()

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
            "external_data": {},  # Hata veren alan eklendi (Boş bir sözlük olarak başlıyor)
            "risk_score": 0.0,
            "is_approved": False,
            "reasons": [],  # Liste alanları boş liste olarak başlatılmalı
            "policy_flags": [],  # Liste alanları boş liste olarak başlatılmalı
            "logs": [],
            "final_decision": None  # Henüz karar verilmediği için None
        }

        config = {"configurable" : {"thread_id": app_id}}

        os.makedirs("data", exist_ok=True)

        async with AsyncSqliteSaver.from_conn_string("data/checkpoints.db") as memory:
            loan_graph = build_graph(memory)

            result = await loan_graph.ainvoke(initial_state, config=config)

            state_snapshot = await loan_graph.aget_state(config)

            if state_snapshot.next:
                insert_application(
                    app_id=app_id,
                    full_name=application.full_name,
                    monthly_income=application.monthly_income,
                    requested_loan=application.requested_loan,
                    credit_score=application.credit_score,
                    risk_score=result.get("risk_score") or 0.0,
                    decision="MANUAL_REVIEW"  # Bu değer kuyrukta görünmesini sağlar
                )
                return {
                    "status": "pending_human_review",
                    "application_id": app_id,
                    "message": "The system has completed the preliminary assessment; we are awaiting manual human approval.",
                    "risk_score": result.get("risk_score"),
                    "logs": result.get("logs")
                }
            else:
                insert_application(
                    app_id=app_id,
                    full_name=application.full_name,
                    monthly_income=application.monthly_income,
                    requested_loan=application.requested_loan,
                    credit_score=application.credit_score,
                    risk_score=result.get("risk_score"),
                    decision=result.get("final_decision"),
                )
                return {
                    "status": "completed",
                    "application_id": app_id,
                    "logs": result.get("logs"),
                    "decision": result.get("final_decision"),
                    "risk_score": result.get("risk_score")
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation Failed: {str(e)}")

@app.post("/resume")
async def resume_evaluation(request: HumanReviewRequest):
    config = {"configurable" : {"thread_id": request.application_id}}

    async with AsyncSqliteSaver.from_conn_string("data/checkpoints.db") as memory:
        loan_graph = build_graph(memory)
        current_state = await loan_graph.aget_state(config)
        if not current_state.next:
            raise HTTPException(status_code=400, detail="There are no pending human approvals for this application.")

        await loan_graph.aupdate_state(
            config,
            {
                "logs": [f"[HITL] Human Decision: {request.human_decision} - {request.human_feedback}"],
                "final_decision": request.human_decision
            }
        )

        final_result = await loan_graph.ainvoke(None, config=config)

    resolve_review(app_id=request.application_id,
                   final_decision=request.human_decision,
                   reviewer="Human Agent",
                   note=request.human_feedback)

    return {
        "status": "completed",
        "final_decision": final_result.get("final_decision"),
        "logs": final_result.get("logs")
    }

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

