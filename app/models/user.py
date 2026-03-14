#app/models/user.py 

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.bot import Bot


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    email: Mapped[str]  = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    elo_rating: Mapped[int] = mapped_column(Integer, default=1000)
    created_at: Mapped[DateTime]  = mapped_column(DateTime, default=datetime.utcnow)

    bots: Mapped[list["Bot"]] = relationship("Bot", back_populates="owner")
