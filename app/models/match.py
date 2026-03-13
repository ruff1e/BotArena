# app/models/match.py
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum



class GameType(str, enum.Enum):
    tictactoe = "tictactoe"


class MatchStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    error = "error"


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column( String, primary_key=True, default=lambda: str(uuid.uuid4()))
    bot_a_id: Mapped[str] = mapped_column(String, ForeignKey("bots.id"), nullable=False)
    bot_b_id: Mapped[str] = mapped_column(String, ForeignKey("bots.id"), nullable=False)
    game_type: Mapped[GameType] = mapped_column(Enum(GameType), nullable=False)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), default=MatchStatus.queued)
    winner_id: Mapped[str | None] = mapped_column(String, ForeignKey("bots.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    turns: Mapped[list["MatchTurn"]] = relationship("MatchTurn", back_populates="match")


class MatchTurn(Base):
    __tablename__ = "match_turns"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id: Mapped[str] = mapped_column(String, ForeignKey("matches.id"), nullable=False)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    player: Mapped[str] = mapped_column(String(1), nullable=False)  # A or B
    move: Mapped[dict] = mapped_column(JSON, nullable=False)
    state_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    match: Mapped["Match"] = relationship("Match", back_populates="turns")