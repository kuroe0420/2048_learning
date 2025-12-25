from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import torch
from torch.utils.data import Dataset, random_split

from .encoding import encode_board


@dataclass
class DatasetInfo:
    max_pow: int = 15


class Twenty48ImitationDataset(Dataset):
    def __init__(self, npz_path: str, max_pow: int = 15, mmap_mode: str | None = "r") -> None:
        self.npz = np.load(npz_path, mmap_mode=mmap_mode)
        self.boards = self.npz["boards"]
        self.actions = self.npz["actions"]
        self.max_pow = int(max_pow)

    def __len__(self) -> int:
        return int(self.actions.shape[0])

    def __getitem__(self, idx: int) -> Tuple[torch.FloatTensor, torch.LongTensor]:
        board = self.boards[idx]
        action = int(self.actions[idx])
        encoded = encode_board(board, max_pow=self.max_pow)
        x = torch.from_numpy(encoded).float()
        y = torch.tensor(action, dtype=torch.long)
        return x, y


def split_dataset(dataset: Dataset, val_ratio: float, seed: int | None = None):
    total = len(dataset)
    val_size = int(total * val_ratio)
    train_size = total - val_size
    generator = torch.Generator()
    if seed is not None:
        generator.manual_seed(int(seed))
    return random_split(dataset, [train_size, val_size], generator=generator)
