from __future__ import annotations

from typing import List

import numpy as np
import torch

from twenty48.ai.expectimax import apply_move

from .encoding import encode_board
from .model import PolicyNet


def _sorted_actions_from_logits(logits: torch.Tensor) -> List[int]:
    probs = torch.softmax(logits, dim=-1).cpu().numpy().tolist()
    return [idx for idx, _ in sorted(enumerate(probs), key=lambda x: x[1], reverse=True)]


def select_action(board: np.ndarray, model: PolicyNet, max_pow: int = 15, device: str | torch.device = "cpu") -> int:
    model.eval()
    device = torch.device(device)
    encoded = encode_board(board, max_pow=max_pow)
    x = torch.from_numpy(encoded).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x)[0]

    for action in _sorted_actions_from_logits(logits):
        _, _, moved = apply_move(board, action)
        if moved:
            return int(action)
    return 0
