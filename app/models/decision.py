from enum import Enum

class Decision(str, Enum):
    APPROVE = 'APPROVE'
    REJECT = 'REJECT'
    MANUAL_REVIEW = 'MANUAL_REVIEW'

class ManualDecision(str, Enum):
    APPROVE = 'MANUAL_APPROVE'
    REJECT = 'MANUAL_REJECT'