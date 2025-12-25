import argparse
import json
import sys
from pathlib import Path

import torch

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from twenty48.env import Twenty48Env
from twenty48.ml.inference import select_action
from twenty48.ml.model import PolicyNet


ACTION_NAMES = {
    0: "UP",
    1: "RIGHT",
    2: "DOWN",
    3: "LEFT",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--max-pow", type=int, default=None)
    args = parser.parse_args()

    model_path = Path(args.model)
    meta_path = model_path.with_name("policy_meta.json")
    max_pow = args.max_pow
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        max_pow = int(meta.get("max_pow", max_pow if max_pow is not None else 15))
    if max_pow is None:
        max_pow = 15

    model = PolicyNet(in_channels=max_pow + 1)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))

    env = Twenty48Env()
    env.reset(seed=args.seed)

    done = False
    step = 0
    while not done:
        action = select_action(env.board, model, max_pow=max_pow)
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
        if args.max_steps is not None and step >= args.max_steps:
            break

    print(f"Final score={env.score} max_tile={int(env.board.max())}")


if __name__ == "__main__":
    main()
