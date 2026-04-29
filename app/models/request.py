from pydantic import BaseModel
from app.models.decision import Decision

class ReviewRequest(BaseModel):
    app_id: str
    decision: Decision
    reviewer: str
    note: str

class HumanReviewRequest(BaseModel):
    application_id: str
    human_decision: str
    human_feedback: str
