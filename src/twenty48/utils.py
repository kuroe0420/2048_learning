from __future__ import annotations

import random


def create_rng(seed: int | None = None) -> random.Random:
    return random.Random(seed)


def clone_rng(rng: random.Random) -> random.Random:
    cloned = random.Random()
    cloned.setstate(rng.getstate())
    return cloned
