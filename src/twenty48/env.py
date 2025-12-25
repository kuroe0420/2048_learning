from __future__ import annotations

import random
from typing import List, Tuple

import numpy as np

from .mechanics import slide_and_merge_line
from .rules import is_done
from .utils import clone_rng, create_rng


class Twenty48Env:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng if rng is not None else create_rng()
        self.board = np.zeros((4, 4), dtype=np.int64)
        self.score = 0
        self.won = False

    def reset(self, seed: int | None = None) -> np.ndarray:
        if seed is not None:
            self.rng = create_rng(seed)
        self.board = np.zeros((4, 4), dtype=np.int64)
        self.score = 0
        self.won = False
        self._spawn_tile()
        self._spawn_tile()
        return self.board.copy()

    def step(self, action: int) -> Tuple[np.ndarray, int, bool, dict]:
        original = self.board.copy()
        moved_board, reward, merged = self._move(action)
        moved = not np.array_equal(original, moved_board)

        spawned = None
        invalid_move = False
        if moved:
            spawned = self._spawn_tile(board=moved_board)
            self.board = moved_board
            self.score += reward
        else:
            self.board = original
            reward = 0
            invalid_move = True

        self.won = bool(self.board.max() >= 2048)
        done = is_done(self.board)
        info = {
            "invalid_move": invalid_move,
            "moved": moved,
            "score": int(self.score),
            "max_tile": int(self.board.max()),
            "won": self.won,
            "spawned": spawned,
            "merged": merged,
        }
        return self.board.copy(), int(reward), bool(done), info

    def render(self, mode: str = "human") -> None:
        if mode != "human":
            raise ValueError(f"Unsupported render mode: {mode}")
        print("+----+----+----+----+")
        for row in self.board:
            print("|" + "|".join(f"{int(val):4d}" if val else "    " for val in row) + "|")
            print("+----+----+----+----+")
        print(f"score={self.score} max_tile={int(self.board.max())}")

    def clone(self) -> "Twenty48Env":
        cloned = Twenty48Env(rng=clone_rng(self.rng))
        cloned.board = self.board.copy()
        cloned.score = int(self.score)
        cloned.won = bool(self.won)
        return cloned

    def _move(self, action: int) -> Tuple[np.ndarray, int, List[dict]]:
        oriented, undo = self._orient(self.board, action)
        new_oriented = np.zeros_like(oriented)
        reward = 0
        merged_info: List[dict] = []
        for i in range(4):
            line, line_reward, merged_vals = slide_and_merge_line(oriented[i, :])
            new_oriented[i, :] = line
            reward += line_reward
            merged_info.append({"row": i, "merged": merged_vals})
        return undo(new_oriented), reward, merged_info

    def _orient(self, board: np.ndarray, action: int):
        if action == 3:  # LEFT
            return board.copy(), lambda b: b
        if action == 1:  # RIGHT
            return np.fliplr(board).copy(), np.fliplr
        if action == 0:  # UP
            return board.T.copy(), lambda b: b.T
        if action == 2:  # DOWN
            return np.fliplr(board.T).copy(), lambda b: np.fliplr(b).T
        raise ValueError(f"Invalid action: {action}")

    def _spawn_tile(self, board: np.ndarray | None = None) -> Tuple[int, int, int] | None:
        target = board if board is not None else self.board
        empties = list(zip(*np.where(target == 0)))
        if not empties:
            return None
        r, c = empties[self.rng.randrange(len(empties))]
        value = 4 if self.rng.random() < 0.1 else 2
        target[r, c] = value
        return int(r), int(c), int(value)
