# tests/test_tictactoe.py
# ngl used ai to write tests
import pytest
from app.engine.games.tictactoe import (
    initial_state,
    is_valid_move,
    apply_move,
    check_winner,
)


def test_initial_state_structure():
    state = initial_state()
    assert state["current_player"] == "A"
    assert state["status"] == "ongoing"
    assert state["turn_number"] == 1
    assert len(state["board"]) == 3
    for row in state["board"]:
        assert row == [None, None, None]


def test_valid_move_accepted():
    state = initial_state()
    assert is_valid_move(state, {"row": 0, "col": 0}) is True


def test_out_of_bounds_rejected():
    state = initial_state()
    assert is_valid_move(state, {"row": 3, "col": 0}) is False
    assert is_valid_move(state, {"row": 0, "col": -1}) is False


def test_occupied_cell_rejected():
    state = initial_state()
    state = apply_move(state, {"row": 0, "col": 0})
    assert is_valid_move(state, {"row": 0, "col": 0}) is False


def test_missing_keys_rejected():
    state = initial_state()
    assert is_valid_move(state, {"row": 0}) is False
    assert is_valid_move(state, {}) is False


def test_move_rejected_when_game_over():
    state = initial_state()
    state = apply_move(state, {"row": 0, "col": 0})  # A
    state = apply_move(state, {"row": 1, "col": 0})  # B
    state = apply_move(state, {"row": 0, "col": 1})  # A
    state = apply_move(state, {"row": 1, "col": 1})  # B
    state = apply_move(state, {"row": 0, "col": 2})  # A wins
    assert is_valid_move(state, {"row": 2, "col": 2}) is False


def test_horizontal_win():
    state = initial_state()
    state = apply_move(state, {"row": 0, "col": 0})  # A
    state = apply_move(state, {"row": 1, "col": 0})  # B
    state = apply_move(state, {"row": 0, "col": 1})  # A
    state = apply_move(state, {"row": 1, "col": 1})  # B
    state = apply_move(state, {"row": 0, "col": 2})  # A wins (top row)
    assert state["status"] == "A_wins"


def test_vertical_win():
    state = initial_state()
    state = apply_move(state, {"row": 0, "col": 0})  # A
    state = apply_move(state, {"row": 0, "col": 1})  # B
    state = apply_move(state, {"row": 1, "col": 0})  # A
    state = apply_move(state, {"row": 1, "col": 1})  # B
    state = apply_move(state, {"row": 2, "col": 0})  # A wins (left column)
    assert state["status"] == "A_wins"


def test_diagonal_win():
    state = initial_state()
    state = apply_move(state, {"row": 0, "col": 0})  # A
    state = apply_move(state, {"row": 0, "col": 1})  # B
    state = apply_move(state, {"row": 1, "col": 1})  # A
    state = apply_move(state, {"row": 0, "col": 2})  # B
    state = apply_move(state, {"row": 2, "col": 2})  # A wins (diagonal)
    assert state["status"] == "A_wins"


def test_draw():
    state = initial_state()
    # X O X
    # X X O
    # O X O  -> draw
    moves = [
        {"row": 0, "col": 0},  # A
        {"row": 0, "col": 1},  # B
        {"row": 0, "col": 2},  # A
        {"row": 1, "col": 2},  # B
        {"row": 1, "col": 0},  # A
        {"row": 2, "col": 0},  # B
        {"row": 1, "col": 1},  # A
        {"row": 2, "col": 2},  # B
        {"row": 2, "col": 1},  # A
    ]
    for move in moves:
        state = apply_move(state, move)
    assert state["status"] == "draw"


def test_apply_move_does_not_mutate_original():
    original = initial_state()
    _ = apply_move(original, {"row": 0, "col": 0})
    assert original["board"][0][0] is None
    assert original["current_player"] == "A"
    assert original["turn_number"] == 1