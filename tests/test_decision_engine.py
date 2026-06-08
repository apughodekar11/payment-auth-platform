"""Engine tests. Note there's no Redis or Postgres here — that's the payoff of
keeping the engine pure. Each test states one rule, including the boundaries,
because off-by-one (> vs >=) is exactly the kind of thing that breaks in prod."""

from app.decision_engine import TransactionFacts, evaluate_transaction, LIMITS
from app.models import Decision

# Shared thresholds so the tests read clearly.
LIMITS = {"max_amount": 5000, "max_transaction_per_window": 5}
    

def test_normal_transaction_is_approved():
    verdict = evaluate_transaction(TransactionFacts(amount=100, recent_transaction_count=1, is_blocked=False), **LIMITS)
    assert verdict.decision == Decision.APPROVE


def test_blocked_card_is_declined():
    verdict = evaluate_transaction(TransactionFacts(amount=100, recent_transaction_count=1, is_blocked=True), **LIMITS)
    assert verdict.decision == Decision.DECLINE
    assert verdict.reason == "card_blocklisted"


def test_amount_over_threshold_is_declined():
    verdict = evaluate_transaction(TransactionFacts(amount=5001, recent_transaction_count=1, is_blocked=False), **LIMITS)
    assert verdict.reason == "amount_over_threshold"


def test_amount_exactly_at_threshold_is_approved():
    # Boundary: 5000 is allowed, only > 5000 declines.
    verdict = evaluate_transaction(TransactionFacts(amount=5000, recent_transaction_count=1, is_blocked=False), **LIMITS)
    assert verdict.decision == Decision.APPROVE


def test_velocity_over_limit_is_declined():
    verdict = evaluate_transaction(TransactionFacts(amount=100, recent_transaction_count=6, is_blocked=False), **LIMITS)
    assert verdict.reason == "velocity_exceeded"


def test_velocity_exactly_at_limit_is_approved():
    verdict = evaluate_transaction(TransactionFacts(amount=100, recent_transaction_count=5, is_blocked=False), **LIMITS)
    assert verdict.decision == Decision.APPROVE


def test_blocked_card_beats_amount_rule():
    verdict = evaluate_transaction(TransactionFacts(amount=9999, recent_transaction_count=1, is_blocked=True), **LIMITS)
    assert verdict.reason == "card_blocklisted"