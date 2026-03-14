# app/routers/bots.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.bot import Bot
from app.schemas.bot import CreateBotRequest, BotResponse, BotDetailResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/bots", tags=["bots"])



#Add a bot to the user
@router.post("/", response_model=BotResponse, status_code=201)
def registerBot(request: CreateBotRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    #first check if the bot with that name already exists
    existing_bot = db.query(Bot).filter(Bot.name == request.name, Bot.user_id == user.id).first()
    if existing_bot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A bot with this name already exists",
        )
        
    bot = Bot(
        user_id = user.id,
        name=request.name,
        language=request.language,
        code = request.code,
    )

    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot

#Get all the bots in the database
@router.get("/", response_model=list[BotResponse], status_code=200)
def get_all_bots(db: Session = Depends(get_db)):

    return db.query(Bot).all()



#Get all the bots from the current user
@router.get("/me", response_model=list[BotDetailResponse], status_code=200)
def get_bots(db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    return db.query(Bot).filter(Bot.user_id == user.id).all()



#Get the bot with id
@router.get("/{bot_id}", response_model=BotResponse, status_code=200)
def get_bot(bot_id: str, db: Session = Depends(get_db)):
    
    bot =  db.query(Bot).filter(Bot.id == bot_id).first()

    #if the bot does not exist, raise 404
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with id: {bot_id} does not exist",
        )
    
    return bot
    


#Delete a bot with bot_id / needs user
@router.delete("/{bot_id}", response_model=None, status_code=204)
def delete_bot(bot_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    bot = db.query(Bot).filter(Bot.id == bot_id).first()

    #check if the bot with that id exists
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot with id: {bot_id} not found"
        )
    
    #then check if the user actually owns the bot 
    if bot.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized action",
        )
    
    db.delete(bot)
    db.commit()

    return None