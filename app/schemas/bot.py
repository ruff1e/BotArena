from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional


class Language(str, Enum):
    python = "python"
    javascript = "javascript"


class CreateBotRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    language: Language
    code: str = Field(min_length=10)


class BotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    language: Language
    elo_rating: int
    win_count: int
    loss_count: int
    draw_count: int 
    created_at: datetime


class BotDetailResponse(BotResponse):
    # Extends BotResponse and adds code
    # Only used for the owner viewing their own bot
    code: str


