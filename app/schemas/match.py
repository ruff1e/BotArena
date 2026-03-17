from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional, Any
from app.schemas.bot import BotResponse



class GameType(str, Enum):
    tictactoe = "tictactoe"


class MatchStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    error = "error"

class CreateMatchRequest(BaseModel):
    bot_a_id: str
    bot_b_id: str
    game_type: GameType


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


    id: str
    bot_a_id: str
    bot_b_id: str
    game_type: GameType
    status: MatchStatus
    winner_id: Optional[str] = None
    created_at: datetime
    finished_at: Optional[datetime] = None



class TurnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    match_id: str
    turn_number: int
    player: str
    move: Any
    state_snapshot: Any
    created_at: datetime