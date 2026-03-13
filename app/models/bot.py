# app/models/bot.py
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum

class Language(str, enum.Enum):
    python = "python"
    javascript = "javascript"

class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[str] = mapped_column( String, primary_key=True, default=lambda: str(uuid.uuid4()) )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    language: Mapped[Language] = mapped_column(Enum(Language), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    elo_rating: Mapped[int] = mapped_column(Integer, default=1000)
    win_count: Mapped[int] = mapped_column(Integer, default=0)
    loss_count: Mapped[int] = mapped_column(Integer, default=0)
    draw_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped["User"] = relationship("User", back_populates="bots")