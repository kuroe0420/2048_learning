from __future__ import annotations

from typing import Dict

import numpy as np

DEFAULT_WEIGHTS: Dict[str, float] = {
    "empty": 2.7,
    "max_tile": 1.0,
    "monotonicity": 1.0,
    "smoothness": 0.1,
}


def _log2_board(board: np.ndarray) -> np.ndarray:
    log_board = np.zeros_like(board, dtype=np.float64)
    mask = board > 0
    if np.any(mask):
        log_board[mask] = np.log2(board[mask])
    return log_board


def _smoothness(log_board: np.ndarray) -> float:
    total = 0.0
    for r in range(4):
        for c in range(4):
            if log_board[r, c] == 0:
                continue
            if c + 1 < 4 and log_board[r, c + 1] > 0:
                total -= abs(log_board[r, c] - log_board[r, c + 1])
            if r + 1 < 4 and log_board[r + 1, c] > 0:
                total -= abs(log_board[r, c] - log_board[r + 1, c])
    return total


def _monotonicity(log_board: np.ndarray) -> float:
    total = 0.0
    for r in range(4):
        inc = 0.0
        dec = 0.0
        for c in range(3):
            if log_board[r, c] > log_board[r, c + 1]:
                dec += log_board[r, c] - log_board[r, c + 1]
            else:
                inc += log_board[r, c + 1] - log_board[r, c]
        total += max(inc, dec)

    for c in range(4):
        inc = 0.0
        dec = 0.0
        for r in range(3):
            if log_board[r, c] > log_board[r + 1, c]:
                dec += log_board[r, c] - log_board[r + 1, c]
            else:
                inc += log_board[r + 1, c] - log_board[r, c]
        total += max(inc, dec)

    return total


def evaluate(board: np.ndarray, score: int, weights: Dict[str, float] | None = None) -> float:
    """Evaluate board desirability for expectimax."""
    used_weights = DEFAULT_WEIGHTS if weights is None else weights
    log_board = _log2_board(board)
    empty_count = float(np.count_nonzero(board == 0))
    max_tile = float(log_board.max()) if np.any(log_board) else 0.0
    smoothness = _smoothness(log_board)
    monotonicity = _monotonicity(log_board)

    return (
        used_weights.get("empty", 0.0) * empty_count
        + used_weights.get("max_tile", 0.0) * max_tile
        + used_weights.get("monotonicity", 0.0) * monotonicity
        + used_weights.get("smoothness", 0.0) * smoothness
    )
