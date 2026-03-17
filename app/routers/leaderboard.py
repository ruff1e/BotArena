# app/routers/leaderboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.leaderboard import BotLeaderboardEntry, UserLeaderboardEntry

from app.database import get_db
from app.models.bot import Bot
from app.models.user import User

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])



@router.get("/bots", response_model=list[BotLeaderboardEntry])
def bot_leaderboard(
    limit: int = 20, offset: int = 0, db: Session = Depends(get_db)
):
    return (
        db.query(Bot)
        .order_by(Bot.elo_rating.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/users", response_model=list[UserLeaderboardEntry])
def user_leaderboard(
    limit: int = 20, offset: int = 0, db: Session = Depends(get_db)
):
    return (
        db.query(User)
        .order_by(User.elo_rating.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )