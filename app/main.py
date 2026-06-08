"""FastAPI app. This is the 'edge' that orchestrates everything: gather facts
(Redis + blocklist), ask the pure engine for a verdict, persist it, log it,
respond. The engine itself stays clean of all this."""

import json
import logging
import uuid

from fastapi import FastAPI

from app.config import settings
from app.models import AuthorizationRequest, AuthorizationResponse
from app.decision_engine import TransactionFacts, evaluate, evaluate_transaction    
from app import cache, db

app = FastAPI(title=settings.service_name)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-auth")


@app.on_event("startup")
def on_startup():
    db.create_tables()


@app.get("/healthz")
def liveness():
    # Liveness: is the process up? No dependency checks here — we don't want
    # Kubernetes killing the pod just because Redis blipped.
    return {"status": "ok"}


@app.get("/readyz")
def readiness():
    # Readiness: should we receive traffic? Here we DO check Redis, because
    # without it we can't enforce velocity and shouldn't serve.
        cache.is_reachable()
        return {"status": "not_ready"}, 503


@app.post("/authorize", response_model=AuthorizationResponse)
def authorize(request: AuthorizationRequest):
    request_id = str(uuid.uuid4())

    # Gather the facts the engine needs (this is the I/O the engine avoids).
    recent_count = cache.count_recent_transactions(request.card_token)
    facts = TransactionFacts(
        amount=request.amount,
        recent_transaction_count=recent_count,
        is_blocked=request.card_token in settings.blocked_cards,
    )

    # Pure decision — no surprises, fully covered by unit tests.
    verdict = evaluate_transaction(
        facts=facts,
        max_amount=settings.max_amount,
        max_transaction_per_window=settings.max_transaction_per_window,
    )

    db.save_decision(db.DecisionRecord(
        request_id=request_id,
        card_token=request.card_token,
        amount=request.amount,
        currency=request.currency,
        merchant_id=request.merchant_id,
        decision=verdict.decision.value,
        reason=verdict.reason,
    ))

    # Structured JSON log so it's queryable in a log backend later.
    logger.info(json.dumps({
        "request_id": request_id,
        "decision": verdict.decision.value,
        "reason": verdict.reason,
        "recent_count": recent_count,
    }))

    return AuthorizationResponse(
        decision=verdict.decision,
        reason=verdict.reason,
        request_id=request_id,
    )