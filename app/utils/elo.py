# app/utils/elo.py


def expected_score(rating_a: int, rating_b: int) -> float:
    # This calculates the expected probability of A winning against B.
    # If both ratings are equal, expected score is 0.5 (50/50).
    # If A is rated much higher, expected score approaches 1.0.
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def calculate_new_ratings(
    rating_a: int, rating_b: int, winner: str, k: int = 32
) -> tuple[int, int]:
    
    #   1.0 = A won
    #   0.0 = A lost
    #   0.5 = draw

    expected_a = expected_score(rating_a, rating_b)

    if winner == "A":
        actual_a = 1.0
    elif winner == "B":
        actual_a = 0.0
    else:
        actual_a = 0.5

    actual_b = 1.0 - actual_a
    expected_b = 1.0 - expected_a

    new_rating_a = round(rating_a + k * (actual_a - expected_a))
    new_rating_b = round(rating_b + k * (actual_b - expected_b))

    return new_rating_a, new_rating_b