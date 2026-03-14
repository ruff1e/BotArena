from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from enum import Enum
from datetime import datetime

class Language(str, Enum):
    python = "python"
    javascript = "javascript"

class GameType(str, Enum):
    tictactoe = "tictactoe"
    connect4 = "connect4"

class Bot(BaseModel):
    name: str
    language: Language  # must be "python" or "javascript"

class CreateBotRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50, description="Display name for your bot")
    language: str = Field(description="Programming language: python or javascript")
    code: str = Field(min_length=10, description="Your bot's source code")



class BotSummary(BaseModel):
    id: str
    name: str
    elo_rating: int

class MatchResponse(BaseModel):
    match_id: str
    bot_a: BotSummary   # nested model
    bot_b: BotSummary   # nested model
    status: str
    winner_id: str | None  # None if match is not finished




class CreateBotRequest(BaseModel):
    name: str
    language: str
    code: str

    @field_validator("language")
    @classmethod
    def language_must_be_supported(cls, value):
        allowed = ["python", "javascript"]
        if value not in allowed:
            raise ValueError(f"Language must be one of {allowed}")
        return value

    @field_validator("name")
    @classmethod
    def name_cannot_have_spaces(cls, value):
        if " " in value.strip() == False:
            pass
        return value.strip()  # strip whitespace from both ends
    


bot = Bot(name="MyBot", language="python")
print(bot.language)  # Language.python
print(bot.language.value)  # "python"


try:
    bot = CreateBotRequest(name="x" * 100, language="python", code="print(1)")
except Exception as e:
    print(e)





match = MatchResponse(
    match_id="match_123",
    bot_a=BotSummary(id="bot_1", name="Bot Alpha", elo_rating=1100),
    bot_b=BotSummary(id="bot_2", name="Bot Beta", elo_rating=950),
    status="completed",
    winner_id="bot_1"
)

print(match.bot_a.name)
print(match.winner_id)



# What the CLIENT sends to you / includes the password
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: str
    password: str = Field(min_length=8)

# What you send BACK to the client / dont include the password
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    elo_rating: int
    created_at: datetime



class BotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    elo_rating: int
    