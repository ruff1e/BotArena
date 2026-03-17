from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional, Any
from app.schemas.bot import BotResponse


class BotLeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    elo_rating: int
    win_count: int
    loss_count: int
    draw_count: int
    user_id: str


class UserLeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    elo_rating: int
    created_at: datetime