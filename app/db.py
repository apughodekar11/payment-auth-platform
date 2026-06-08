from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings

# pool_pre_ping checks a connection is alive before using it, which avoids errors
# from stale connections after the DB restarts.
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class DecisionRecord(Base):
    __tablename__ = "decisions"

    request_id: Mapped[str] = mapped_column(String, primary_key=True)
    card_token: Mapped[str] = mapped_column(String, index=True)   # indexed: we query by card
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    merchant_id: Mapped[str] = mapped_column(String)
    decision: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


def create_tables() -> None:
    # Fine for a demo. In production this would be an Alembic migration, not
    # create_all on startup — say so if asked.
    Base.metadata.create_all(engine)


def save_decision(record: DecisionRecord) -> None:
    with SessionFactory() as session:
        session.add(record)
        session.commit()