import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from twenty48.env import Twenty48Env


def main() -> None:
    env = Twenty48Env()
    env.reset(seed=0)
    rng = random.Random(0)
    steps = 0
    done = False
    while not done and steps < 1000:
        action = rng.randrange(4)
        _, _, done, _ = env.step(action)
        steps += 1
    env.render()
    print(f"steps={steps} done={done} score={env.score}")


if __name__ == "__main__":
    main()
