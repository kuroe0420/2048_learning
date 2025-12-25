# 2048-ai

A small, deterministic 2048 environment intended for search and reinforcement learning.

## Documentation

- SSOT (spec/progress): `docs/`
- Archive: `docs/archive/` (reference only)

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
- Progress: `docs/PROGRESS.md`
- Status output: `python scripts/status.py`
- Test runner: `python scripts/run_tests.py`
- Random play: `python scripts/play_random.py`
- Benchmark: `python scripts/benchmark.py`
- Train policy (GPU auto): `python scripts/train_policy.py --dataset data/raw/dataset.npz --device auto`
- Simulate (random): `python scripts/simulate.py --agent random -n 200 --seed 0`
- Simulate (expectimax): `python scripts/simulate.py --agent expectimax -n 50 --depth 3 --seed 0`
- Simulate (policy): `python scripts/simulate.py --agent policy -n 200 --model data/models/policy_best.pt --seed 0`
