from enum import Enum

class Decision(str, Enum):
    APPROVE = 'APPROVE'
    REJECT = 'REJECT'
    MANUAL_REVIEW = 'MANUAL_REVIEW'
    MANUAL_APPROVE = 'MANUAL_APPROVE'
    MANUAL_REJECT = 'MANUAL_REJECT'
