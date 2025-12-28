import argparse
import json
import sys
import time
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
    parser.add_argument("--device", type=str, default="auto", help="auto|cpu|cuda")
    parser.add_argument("--log-file", type=str, default=".artifacts/play_policy_seed0.log")
    parser.add_argument("--summary-json", type=str, default=".artifacts/play_policy_summary.json")
    parser.add_argument("--print-steps", type=int, default=50)
    args = parser.parse_args()

    model_path = Path(args.model)
    meta_path = model_path.with_name("policy_meta.json")
    max_pow = args.max_pow
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        max_pow = int(meta.get("max_pow", max_pow if max_pow is not None else 15))
    if max_pow is None:
        max_pow = 15

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = PolicyNet(in_channels=max_pow + 1).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))

    env = Twenty48Env()
    env.reset(seed=args.seed)

    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "\n".join(
            [
                "play_policy log",
                f"model={model_path}",
                f"seed={args.seed}",
                f"max_steps={args.max_steps}",
                f"device={device}",
                f"max_pow={max_pow}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    start_time = time.perf_counter()
    done = False
    step = 0
    invalid_count = 0
    while not done:
        action = select_action(env.board, model, max_pow=max_pow, device=device)
        _, reward, done, info = env.step(action)
        if info["invalid_move"]:
            invalid_count += 1
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
        if step < args.print_steps:
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    "step={step} action={action} reward={reward} score={score} max_tile={max_tile} invalid={invalid}\n".format(
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

    elapsed = time.perf_counter() - start_time
    print(f"Final score={env.score} max_tile={int(env.board.max())}")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"elapsed_sec={elapsed:.3f}\n")

    summary = {
        "final_score": int(env.score),
        "max_tile": int(env.board.max()),
        "steps": int(step),
        "invalid_count": int(invalid_count),
        "invalid_rate": float(invalid_count / max(1, step)),
        "model": str(model_path),
        "seed": args.seed,
        "max_steps": args.max_steps,
        "duration_ms": int(elapsed * 1000),
    }
    Path(args.summary_json).write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
