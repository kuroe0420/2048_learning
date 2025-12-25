from __future__ import annotations

import numpy as np


def has_moves(board: np.ndarray) -> bool:
    if np.any(board == 0):
        return True

    for r in range(4):
        for c in range(3):
            if board[r, c] == board[r, c + 1]:
                return True

    for r in range(3):
        for c in range(4):
            if board[r, c] == board[r + 1, c]:
                return True

    return False


def is_done(board: np.ndarray) -> bool:
    return not has_moves(board)
