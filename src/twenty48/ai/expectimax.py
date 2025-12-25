from __future__ import annotations

import random
from typing import Dict, List, Tuple

import numpy as np

from twenty48.mechanics import slide_and_merge_line
from twenty48.rules import is_done

from .heuristics import evaluate

ActionValue = Tuple[int, float]


def choose_action(env, depth: int, max_cells: int = 4) -> int:
    """env??????????action(0-3)????"""
    board = env.board
    score = int(env.score)

    cache: Dict[Tuple[str, int, Tuple[int, ...], int], float] = {}
    action_order = [3, 2, 0, 1]

    best_action = 0
    best_value = float("-inf")
    for action in action_order:
        new_board, delta, moved = apply_move(board, action)
        if not moved:
            continue
        value = chance_value(new_board, score + delta, depth - 1, cache, max_cells=max_cells)
        if value > best_value:
            best_value = value
            best_action = action

    return best_action


def apply_move(board: np.ndarray, action: int) -> Tuple[np.ndarray, int, bool]:
    oriented, undo = _orient_for_action(board, action)
    new_oriented = np.zeros_like(oriented)
    reward = 0
    for i in range(4):
        line, line_reward, _ = slide_and_merge_line(oriented[i, :])
        new_oriented[i, :] = line
        reward += line_reward
    new_board = undo(new_oriented)
    moved = not np.array_equal(board, new_board)
    return new_board, int(reward), moved


def max_value(board: np.ndarray, score: int, depth: int, cache: Dict, max_cells: int = 4) -> float:
    key = ("max", depth, _board_key(board), score)
    cached = cache.get(key)
    if cached is not None:
        return cached

    if depth == 0 or is_done(board):
        value = float(evaluate(board, score))
        cache[key] = value
        return value

    best = float("-inf")
    for action in (3, 2, 0, 1):
        new_board, delta, moved = apply_move(board, action)
        if not moved:
            continue
        value = chance_value(new_board, score + delta, depth - 1, cache, max_cells=max_cells)
        if value > best:
            best = value

    if best == float("-inf"):
        best = float(evaluate(board, score))

    cache[key] = best
    return best


def chance_value(board: np.ndarray, score: int, depth: int, cache: Dict, max_cells: int = 4) -> float:
    key = ("chance", depth, _board_key(board), score)
    cached = cache.get(key)
    if cached is not None:
        return cached

    empties = list(zip(*np.where(board == 0)))
    if not empties:
        value = max_value(board, score, depth, cache, max_cells=max_cells)
        cache[key] = value
        return value

    if len(empties) > max_cells:
        rng = random.Random(_sample_seed(board, score, depth))
        empties = rng.sample(empties, k=max_cells)

    total = 0.0
    for r, c in empties:
        for value, prob in ((2, 0.9), (4, 0.1)):
            next_board = board.copy()
            next_board[r, c] = value
            total += prob * max_value(next_board, score, depth, cache, max_cells=max_cells)

    value = total / len(empties)
    cache[key] = value
    return value


def _board_key(board: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(x) for x in board.reshape(-1))


def _sample_seed(board: np.ndarray, score: int, depth: int) -> int:
    return int((score + depth * 1315423911 + int(board.sum())) & 0xFFFFFFFF)


def _orient_for_action(board: np.ndarray, action: int):
    if action == 3:
        return board.copy(), lambda b: b
    if action == 1:
        return np.fliplr(board).copy(), np.fliplr
    if action == 0:
        return board.T.copy(), lambda b: b.T
    if action == 2:
        return np.fliplr(board.T).copy(), lambda b: np.fliplr(b).T
    raise ValueError(f"Invalid action: {action}")
