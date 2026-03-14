# /engine/games/tictactoe.py
import copy


def initial_state():
    return {
        "board": [
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ],
        "current_player": "A",
        "status": "ongoing",
        "turn_number": 1,
    }


def is_valid_move(state, move):

    #First if the game is not ongoing, return False immedietly
    if state["status"] != "ongoing":
        return False
    
    row = move.get("row")
    col = move.get("col")

    #If the move is missing return false
    if row is None or col is None:
        return False
    
    #If the player tries to go out of bounds, return False
    if not (0 <= row <= 2 and 0 <= col <= 2):
        return False

    #If the bot is trying to play on a square that's already taken, reject it, return false
    if state["board"][row][col] is not None:
        return False
    
    return True



def check_winner(state):
    #This function return 1 of 4 things
    #It return "A" if player A has 3 in a row
    #It return "B" if player B has 3 in a row
    #it return "draw" if the board is full
    #Return "None" if the game is still going, no winner yet
    board = state["board"]

    # check rows and columns
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] is not None:
            return board[i][0] # Returns "A" or "B"
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i] # Returns "A" or "B"

    # check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0] # Returns "A" or "B"
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2] # Returns "A" or "B"
    
    # check draw (no empty cells left)
    for row in board:
        if None in row:
            return None # the game is still going

    #If there is no winner and alll the rows are full the game is a draw
    return "draw"



def apply_move(state, move):

    #Make a copy of the game
    new_state = copy.deepcopy(state)
    row = move["row"]
    col = move["col"]

    #Keep track fo the current player
    current = new_state["current_player"]

    #Place the current players mark ("A" or "B") on the board
    new_state["board"][row][col] = current
    new_state["turn_number"] += 1

    #Check if this move ended the game or not.
    result = check_winner(new_state)

    if result == "draw":
        new_state["status"] = "draw"
    elif result is not None:
        new_state["status"] = f"{result}_wins"
    else:
        new_state["status"] = "ongoing"
        new_state["current_player"] = "B" if current == "A" else "A"  # Flip the turns

    return new_state
