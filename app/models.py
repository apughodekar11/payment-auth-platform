from enum import Enum
from pydantic import BaseModel, Field

class Decision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "DECLINE"

class AuthorizationRequest(BaseModel):
    card_token: str = Field(min_length=4) # card token must be at least 4 characters long
    amount: float = Field(gt=0) # amount must be greater than 0
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    merchant_id: str = Field(min_length=1)

class AuthorizationResponse(BaseModel):
    decision: Decision
    reason: str # machine-readable reason for the decision, e.g. "amount_exceeds_threshold" or "velocity_limit_exceeded"
    request_id: str # lets us trace one decision through the logs / DB
