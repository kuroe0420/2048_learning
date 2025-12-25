from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np


def slide_and_merge_line(line: Iterable[int]) -> Tuple[np.ndarray, int, List[int]]:
    """Slide a single line to the left and merge equal tiles once per move."""
    tiles = [int(x) for x in line if int(x) != 0]
    merged_values: List[int] = []
    output: List[int] = []
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            new_val = tiles[i] * 2
            output.append(new_val)
            merged_values.append(new_val)
            i += 2
        else:
            output.append(tiles[i])
            i += 1

    output.extend([0] * (4 - len(output)))
    return np.array(output, dtype=np.int64), int(sum(merged_values)), merged_values
