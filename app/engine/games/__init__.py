from app.engine.games import tictactoe

GAME_REGISTRY = {
    "tictactoe": tictactoe,
}

def get_game(game_type: str):
    if game_type not in GAME_REGISTRY:
        raise ValueError(f"Unsupported game type: {game_type}")
    return GAME_REGISTRY[game_type]