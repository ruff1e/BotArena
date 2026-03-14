# app/main.pey

from fastapi import FastAPI
from app.routers import auth, bots


app = FastAPI(title="Bot Arena", version="0.1.0")

app.include_router(auth.router)
app.include_router(bots.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def mainPage():
    return {"status": "main page"}

