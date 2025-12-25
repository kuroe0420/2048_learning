import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from twenty48.env import Twenty48Env
from twenty48.ai.expectimax import choose_action


ACTION_NAMES = {
    0: "UP",
    1: "RIGHT",
    2: "DOWN",
    3: "LEFT",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    env = Twenty48Env()
    env.reset(seed=args.seed)

    done = False
    step = 0
    while not done:
        action = choose_action(env, args.depth)
        _, reward, done, info = env.step(action)
        print(
            "Step {step} | action={action} | reward={reward} | score={score} | max_tile={max_tile} | "
            "invalid={invalid}".format(
                step=step,
                action=ACTION_NAMES.get(action, str(action)),
                reward=reward,
                score=info["score"],
                max_tile=info["max_tile"],
                invalid=info["invalid_move"],
            )
        )
        step += 1

    print(f"Final score={env.score} max_tile={int(env.board.max())}")


if __name__ == "__main__":
    main()
