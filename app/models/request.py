from pydantic import BaseModel
from app.models.decision import ManualDecision

class ReviewRequest(BaseModel):
    app_id: str
    decision: ManualDecision
    reviewer: str
    note: str
