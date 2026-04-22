from enum import Enum

class Decision(str, Enum):
    APPROVE = 'APPROVE'
    REJECT = 'REJECT'
    MANUAL_REVIEW = 'MANUAL_REVIEW'
