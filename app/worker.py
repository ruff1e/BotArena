# app/worker.py
import json
from datetime import datetime, timezone

from celery import Celery
import redis as redis_lib

from app.config import settings
from app.database import SessionLocal
from app.models.match import Match, MatchTurn, MatchStatus
from app.models.bot import Bot
from app.engine.referee import run_match
from app.utils.elo import calculate_new_ratings


# Initialize the Celery app.
# The broker is Redis — Celery uses it to receive tasks.
# The backend is also Redis — Celery uses it to store task results.
celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@celery_app.task(name="run_match_task")
def run_match_task(match_id: str):
    # This task is triggered when a user creates a match via POST /matches.
    # It runs the entire match from start to finish asynchronously

    # Each Celery task needs its own DB session
    db = SessionLocal()

    try:
        # Fetch the match and both bots from the database.
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            print(f"[worker] Match: {match_id} not found.")
            return

        bot_a = db.query(Bot).filter(Bot.id == match.bot_a_id).first()
        bot_b = db.query(Bot).filter(Bot.id == match.bot_b_id).first()

        if not bot_a or not bot_b:
            print(f"[worker] One or both bots not found for match: {match_id}.")
            match.status = MatchStatus.error
            db.commit()
            return

        # Mark the match as running so the API can reflect this.
        match.status = MatchStatus.running
        db.commit()

        print(f"[worker] Starting match {match_id}: {bot_a.name} vs {bot_b.name}")



        # The referee calls this after every valid turn.
        # It saves the turn to the database and publishes the state to a Redis pub/sub channel for live WebSocket viewers.
        redis_client = redis_lib.from_url(settings.redis_url)

        def on_turn(turn_data: dict):
            # Save the turn to match_turns table.
            turn = MatchTurn(
                match_id=match_id,
                turn_number=turn_data["turn_number"],
                player=turn_data["player"],
                move=turn_data["move"],
                state_snapshot=turn_data["state"],
            )
            db.add(turn)
            db.commit()

            # Publish the turn to Redis pub/sub.
            # The WebSocket endpoint subscribes to this channel and forwards updates to connected browsers.
            channel = f"match:{match_id}"
            redis_client.publish(channel, json.dumps({
                "turn_number": turn_data["turn_number"],
                "player": turn_data["player"],
                "move": turn_data["move"],
                "state": turn_data["state"],
            }))

        #run the match
        result = run_match(
            bot_a_code=bot_a.code,
            bot_a_language=bot_a.language.value,
            bot_b_code=bot_b.code,
            bot_b_language=bot_b.language.value,
            game_type=match.game_type.value,
            on_turn=on_turn,
        )

        # save the result
        winner = result["winner"]

        if winner == "A":
            match.winner_id = bot_a.id
        elif winner == "B":
            match.winner_id = bot_b.id
        else:
            match.winner_id = None  #draw

        match.status = MatchStatus.completed
        match.finished_at = datetime.now(timezone.utc)

        if winner == "A":
            bot_a.win_count += 1
            bot_b.loss_count += 1
        elif winner == "B":
            bot_b.win_count += 1
            bot_a.loss_count += 1
        else:
            bot_a.draw_count += 1
            bot_b.draw_count += 1

        #Update elo
        new_elo_a, new_elo_b = calculate_new_ratings(
            bot_a.elo_rating, bot_b.elo_rating, winner
        )
        bot_a.elo_rating = new_elo_a
        bot_b.elo_rating = new_elo_b

        db.commit()

        # Publish a final message so WebSocket clients know that the match ended.
        redis_client.publish(f"match:{match_id}", json.dumps({
            "event": "match_over",
            "winner": winner,
            "final_state": result["final_state"],
        }))

        print(f"[worker] Match {match_id} completed. Winner: {winner}")

    except Exception as e:
        print(f"[worker] Unexpected error in match {match_id}: {e}")
        match.status = MatchStatus.error
        db.commit()

    finally:
        db.close()