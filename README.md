# 2048-ai

A small, deterministic 2048 environment intended for search and reinforcement learning.

## Usage

Action mapping:
- 0 = UP
- 1 = RIGHT
- 2 = DOWN
- 3 = LEFT

Example:

```python
from twenty48.env import Twenty48Env

env = Twenty48Env()
obs = env.reset(seed=0)
obs, reward, done, info = env.step(3)
env.render()
```

## Development

- Run tests: `pytest -q`
- Random play: `python scripts/play_random.py`
- Benchmark: `python scripts/benchmark.py`
