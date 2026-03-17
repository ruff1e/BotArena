# app/routers/matches.py

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from uuid import UUID
import json
import redis.asyncio as aioredis

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.bot import Bot
from app.models.match import Match, MatchTurn
from app.schemas.match import CreateMatchRequest, MatchResponse, TurnResponse
from app.worker import celery_app, run_match_task
from app.config import settings


router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/", response_model=MatchResponse)
def create_match(payload: CreateMatchRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    bot_a = db.query(Bot).filter(Bot.id == payload.bot_a_id).first()
    bot_b = db.query(Bot).filter(Bot.id == payload.bot_b_id).first()

    if not bot_a:
        raise HTTPException(status_code=404, detail="Bot A not found")
    if not bot_b:
        raise HTTPException(status_code=404, detail="Bot B not found")
    if bot_a.id == bot_b.id:
        raise HTTPException(status_code=400, detail="A bot cannot fight itself")


    match = Match(
        bot_a_id=bot_a.id,
        bot_b_id=bot_b.id,
        game_type=payload.game_type,
        status="queued",
    )
    db.add(match)
    db.commit()
    db.refresh(match)

    # match runs in the background
    run_match_task.delay(str(match.id))

    return match


@router.get("/", response_model=list[MatchResponse])
def list_matches(bot_id: UUID = None, user_id: UUID = None, limit: int = 20, offset: int = 0, db: Session = Depends(get_db) ):


    query = db.query(Match)

    if bot_id:
        query = query.filter((Match.bot_a_id == bot_id) | (Match.bot_b_id == str(bot_id)))

    if user_id:
        user_bot_ids = [
            b.id
            for b in db.query(Bot.id).filter(Bot.user_id == str(user_id)).all()
        ]
        query = query.filter((Match.bot_a_id.in_(user_bot_ids))| (Match.bot_b_id.in_(user_bot_ids)))

    return (
        query.order_by(Match.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: UUID, db: Session = Depends(get_db)):

    match = db.query(Match).filter(Match.id == str(match_id)).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.get("/{match_id}/replay", response_model=list[TurnResponse])
def get_replay(match_id: UUID, db: Session = Depends(get_db)):

    match = db.query(Match).filter(Match.id == str(match_id)).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status not in ["completed", "error"]:
        raise HTTPException(status_code=400, detail="Match is not finished yet")

    return (
        db.query(MatchTurn)
        .filter(MatchTurn.match_id == str(match_id))
        .order_by(MatchTurn.turn_number.asc())
        .all()
    )


@router.websocket("/{match_id}/live")
async def live_match(match_id: UUID, websocket: WebSocket):

    await websocket.accept()

    redis = aioredis.from_url(settings.redis_url)
    pubsub = redis.pubsub()
    channel = f"match:{match_id}"

    await pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            # only forward actual data messages
            if message["type"] != "message":
                continue

            data = json.loads(message["data"].decode())
            await websocket.send_text(json.dumps(data))

            # Close the connection once the match is over
            if data.get("event") == "match_over":
                break

    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await redis.aclose()