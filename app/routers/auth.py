# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):

    #First check if the username is already in use
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is taken.",
        )

    #Then check if email is already registered
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered",
        )

    #If email and username is not taken then create the user
    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
    )
    #then add the user to the database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user



@router.post("/login", response_model=TokenResponse, status_code=200)
def login(request: LoginRequest, db: Session = Depends(get_db)):

    #find the user with their username
    user = db.query(User).filter(User.username == request.username).first()

    #Then verify that the user exists and the password is correct
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invlaid username or password",
        )
    
    #Generate the JWT token
    token = create_access_token(data={"sub": user.id})

    return TokenResponse(access_token=token)