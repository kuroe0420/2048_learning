import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from twenty48.env import Twenty48Env


def play_game(seed: int) -> int:
    env = Twenty48Env()
    env.reset(seed=seed)
    done = False
    steps = 0
    while not done and steps < 5000:
        action = env.rng.randrange(4)
        _, _, done, _ = env.step(action)
        steps += 1
    return env.score


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--games", type=int, default=100)
    args = parser.parse_args()

    scores = [play_game(seed) for seed in range(args.games)]
    avg_score = sum(scores) / len(scores)
    print(f"games={args.games} avg_score={avg_score:.2f} max_score={max(scores)}")


if __name__ == "__main__":
    main()
