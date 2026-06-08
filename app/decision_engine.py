from dataclasses import dataclass
from app.models import Decision

@dataclass(frozen=True)
class TransactionFacts:
    amount : float
    recent_transaction_count: int 
    is_blocked: bool

@dataclass(frozen=True)
class evaluate:
    decision: Decision
    reason: str

def evaluate_transaction(facts: TransactionFacts, *, max_amount: float, max_transaction_per_window: int) -> evaluate:
    if facts.is_blocked:
        return evaluate(Decision.REJECT, "card_blocked")
    if facts.amount > max_amount:
        return evaluate(Decision.REJECT, "amount_over_threshold")
    if facts.recent_transaction_count > max_transaction_per_window:
        return evaluate(Decision.REJECT, "velocity_limit_exceeded")
    return evaluate(Decision.APPROVE, "approved")