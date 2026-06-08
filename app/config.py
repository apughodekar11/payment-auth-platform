"""Central settings. Everything that changes between local and cloud lives here
as an env var so the same image runs anywhere without code changes."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Defaults point at the docker-compose service names ("db", "redis") so the
    # stack runs with zero config locally. Kubernetes overrides these via ConfigMap.
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/payments"
    redis_url: str = "redis://redis:6379/0"

    # Fraud rule thresholds. Kept as config, not constants, so they can be tuned
    # per environment without a redeploy of the logic.
    max_amount: float = 5000
    velocity_window_seconds: int = 60   # how long a card's counter survives
    max_transaction_per_window: int = 5        # decline once a card exceeds this

    # A tuple (not a set) so it's immutable once loaded.
    blocked_cards: tuple[str, ...] = ("tok_blocked",)

    # Observability wiring is off by default; flipped on in the cloud (Phase 7).
    otel_enabled: bool = False
    otel_endpoint: str = ""
    otel_headers: str = ""
    service_name: str = "payment-auth"


settings = Settings()