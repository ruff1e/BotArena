# app/main.pey

from pydoc import text

from fastapi import FastAPI
from app.database import SessionLocal
from app.routers import auth, bots, matches, leaderboard
import redis as redis_lib
from app.config import settings


app = FastAPI(title="Bot Arena", version="0.1.0")

app.include_router(auth.router)
app.include_router(bots.router)
app.include_router(matches.router)
app.include_router(leaderboard.router)


@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    # check redis
    try:
        r = redis_lib.from_url(settings.redis_url)
        r.ping()
        redis_status = "ok"
    except Exception as e:
        redis_status = f"error: {e}"

    healthy = db_status == "ok" and redis_status == "ok"

    return {
        "status": "ok" if healthy else "degraded",
        "database": db_status,
        "redis": redis_status,
    }

