from __future__ import annotations

import numpy as np


def encode_board(board: np.ndarray, max_pow: int = 15) -> np.ndarray:
    """One-hot encode board into (C, 4, 4), C=max_pow+1.

    Channel 0 represents empty, channel k represents tile value 2**k.
    Values above max_pow are clamped into max_pow channel.
    """
    channels = max_pow + 1
    encoded = np.zeros((channels, 4, 4), dtype=np.float32)

    empties = board == 0
    if np.any(empties):
        encoded[0][empties] = 1.0

    nonzero = board > 0
    if np.any(nonzero):
        powers = np.log2(board[nonzero]).astype(np.int64)
        powers = np.clip(powers, 1, max_pow)
        rows, cols = np.where(nonzero)
        for r, c, p in zip(rows, cols, powers):
            encoded[p, r, c] = 1.0

    return encoded
