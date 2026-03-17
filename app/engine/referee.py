# app/engine/referee.py

from app.engine.sandbox import get_bot_move
from app.engine.games import get_game


def run_match(bot_a_code: str, bot_a_language: str, bot_b_code: str, bot_b_language: str, game_type: str = "tictactoe", on_turn=None) -> dict:
    # on_turn is an optional callback function the worker will pass in later.
    # After each turn it gets called with the turn data so the worker can
    # save it to the database and broadcast it via WebSocket.
    # During testing just pass None and ignore it.

    game = get_game(game_type)
    state = game.initial_state()

    # Map player letters to their code and language
    bots = {
        "A": {"code": bot_a_code, "language": bot_a_language},
        "B": {"code": bot_b_code, "language": bot_b_language},
    }

    winner = None
    turn_number = 0
    disqualified = False

    while state["status"] == "ongoing":
        current_player = state["current_player"]
        bot = bots[current_player]

        try:
            move = get_bot_move(
                language=bot["language"],
                code=bot["code"],
                state_dict=state,
                timeout_seconds=5,
            )
        except TimeoutError:
            # Bot took too long / it loses immediately.
            print(f"[referee] Player {current_player} timed out.")
            winner = "B" if current_player == "A" else "A"
            disqualified = True
            break

        # Validate the move before applying it.
        # If a bot sends back a valid JSON but an illegal move it loses immediately.
        if not game.is_valid_move(state, move):
            print(f"[referee] Player {current_player} made an invalid move: {move}")
            winner = "B" if current_player == "A" else "A"
            disqualified = True
            break

        # Apply the move and get the new state.
        state = game.apply_move(state, move)
        turn_number += 1

        # If a worker callback was provided, call it with turn data.
        # This is how the worker will save turns to the DB and broadcast via WebSocket
        if on_turn:
            on_turn({
                "turn_number": turn_number,
                "player": current_player,
                "move": move,
                "state": state,
            })

    # If nobody was disqualified, read the winner from the final state.
    if not disqualified:
        if state["status"] == "A_wins":
            winner = "A"
        elif state["status"] == "B_wins":
            winner = "B"
        else:
            winner = "draw"

    return {
        "winner": winner,
        "final_state": state,
        "turns": turn_number,
        "disqualified": disqualified,
    }