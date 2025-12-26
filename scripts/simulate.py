import argparse
import csv
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from twenty48.env import Twenty48Env
from twenty48.ai.expectimax import apply_move, choose_action
from twenty48.ml.inference import select_action
from twenty48.ml.model import PolicyNet
import torch


def _parse_seeds(seeds_str: str | None) -> list[int] | None:
    if not seeds_str:
        return None
    parts = [s.strip() for s in seeds_str.split(",") if s.strip()]
    return [int(p) for p in parts]


def _valid_actions(board) -> list[int]:
    actions = []
    for action in (0, 1, 2, 3):
        _, _, moved = apply_move(board, action)
        if moved:
            actions.append(action)
    return actions


def run_one_game(
    agent: str,
    seed: int,
    max_steps: int,
    depth: int,
    model=None,
    device: str = "cpu",
    max_pow: int = 15,
    max_cells: int = 4,
) -> dict:
    env = Twenty48Env()
    env.reset(seed=seed)

    rng = random.Random(seed)
    invalid_count = 0
    moved_steps = 0
    steps = 0
    start = time.perf_counter()

    done = False
    while not done and steps < max_steps:
        if agent == "random":
            actions = _valid_actions(env.board)
            if not actions:
                break
            action = rng.choice(actions)
        elif agent == "expectimax":
            action = choose_action(env, depth, max_cells=max_cells)
        elif agent == "policy":
            action = select_action(env.board, model, max_pow=max_pow, device=device)
        else:
            raise ValueError(f"Unknown agent: {agent}")

        _, _, moved = apply_move(env.board, action)
        if moved:
            moved_steps += 1

        _, _, done, info = env.step(action)
        if info.get("invalid_move"):
            invalid_count += 1
        steps += 1

    duration_ms = (time.perf_counter() - start) * 1000.0
    final_score = int(env.score)
    max_tile = int(env.board.max())
    invalid_rate = float(invalid_count / max(1, steps))

    return {
        "seed": int(seed),
        "final_score": final_score,
        "max_tile": max_tile,
        "steps": int(steps),
        "invalid_count": int(invalid_count),
        "invalid_rate": invalid_rate,
        "duration_ms": float(duration_ms),
        "moved_steps": int(moved_steps),
    }


def _summary_stats(scores: np.ndarray, max_tiles: np.ndarray, invalid_rates: np.ndarray, durations: np.ndarray) -> dict:
    p10, p50, p90, p99 = np.percentile(scores, [10, 50, 90, 99])
    summary = {
        "games": int(scores.size),
        "mean_score": float(np.mean(scores)),
        "median_score": float(np.median(scores)),
        "std_score": float(np.std(scores)),
        "p10": float(p10),
        "p50": float(p50),
        "p90": float(p90),
        "p99": float(p99),
        "mean_max_tile": float(np.mean(max_tiles)),
        "rate_128": float(np.mean(max_tiles >= 128)),
        "rate_256": float(np.mean(max_tiles >= 256)),
        "rate_512": float(np.mean(max_tiles >= 512)),
        "rate_1024": float(np.mean(max_tiles >= 1024)),
        "rate_2048": float(np.mean(max_tiles >= 2048)),
        "rate_4096": float(np.mean(max_tiles >= 4096)),
        "rate_8192": float(np.mean(max_tiles >= 8192)),
        "mean_invalid_rate": float(np.mean(invalid_rates)),
        "total_duration_sec": float(np.sum(durations) / 1000.0),
        "avg_game_duration_ms": float(np.mean(durations)),
    }
    return summary


def _print_summary(agent: str, summary: dict, quiet: bool) -> None:
    if quiet:
        print(
            f"{agent} games={summary['games']} mean={summary['mean_score']:.1f} "
            f"p50={summary['p50']:.1f} p90={summary['p90']:.1f} "
            f"rate_2048={summary['rate_2048']:.3f} invalid={summary['mean_invalid_rate']:.4f}"
        )
        return

    print("Summary")
    for key in [
        "games",
        "mean_score",
        "median_score",
        "std_score",
        "p10",
        "p50",
        "p90",
        "p99",
        "mean_max_tile",
        "rate_128",
        "rate_256",
        "rate_512",
        "rate_1024",
        "rate_2048",
        "rate_4096",
        "rate_8192",
        "mean_invalid_rate",
        "total_duration_sec",
        "avg_game_duration_ms",
    ]:
        value = summary[key]
        if isinstance(value, float):
            print(f"- {key}: {value:.4f}")
        else:
            print(f"- {key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=str, choices=["random", "expectimax", "policy"], required=True)
    parser.add_argument("-n", "--games", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seeds", type=str, default=None)
    parser.add_argument("--max-steps", type=int, default=20000)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--max-cells", type=int, default=4)
    parser.add_argument("--model", type=str, default="data/models/policy_best.pt")
    parser.add_argument("--out-json", type=str, default=None)
    parser.add_argument("--out-csv", type=str, default=None)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    seeds = _parse_seeds(args.seeds)
    if seeds is None:
        seeds = [args.seed + i for i in range(args.games)]
    elif not args.quiet:
        print("[warn] --seeds is provided, ignoring --games")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifacts = Path(".artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)

    out_json = Path(args.out_json) if args.out_json else artifacts / f"simulate_{args.agent}_{ts}.json"
    out_csv = Path(args.out_csv) if args.out_csv else artifacts / f"simulate_{args.agent}_{ts}.csv"

    model = None
    device = "cpu"
    max_pow = 15
    if args.agent == "policy":
        model_path = Path(args.model)
        if not model_path.exists():
            raise FileNotFoundError(f"model not found: {model_path}")
        meta_path = model_path.with_name("policy_meta.json")
        if not meta_path.exists():
            meta_path = model_path.with_suffix(".meta.json")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            max_pow = int(meta.get("max_pow", max_pow))
        model = PolicyNet(in_channels=max_pow + 1)
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()

    per_game = []
    total_games = len(seeds)
    progress_every = 5 if total_games < 50 else 10
    start_all = time.perf_counter()
    for idx, seed in enumerate(seeds, start=1):
        result = run_one_game(
            agent=args.agent,
            seed=int(seed),
            max_steps=args.max_steps,
            depth=args.depth,
            model=model,
            device=device,
            max_pow=max_pow,
            max_cells=args.max_cells,
        )
        per_game.append(result)
        if not args.quiet and (idx % progress_every == 0 or idx == total_games):
            scores_so_far = np.array([g["final_score"] for g in per_game], dtype=np.float64)
            p50 = float(np.percentile(scores_so_far, 50))
            p90 = float(np.percentile(scores_so_far, 90))
            mean_score = float(np.mean(scores_so_far))
            invalid_rate = float(np.mean([g["invalid_rate"] for g in per_game]))
            elapsed = time.perf_counter() - start_all
            avg_per_game = elapsed / idx
            remaining = max(0.0, (total_games - idx) * avg_per_game)
            pct = (idx / total_games) * 100.0
            print(
                f"[{idx}/{total_games} {pct:.1f}%] mean={mean_score:.1f} p50={p50:.1f} "
                f"p90={p90:.1f} invalid={invalid_rate:.4f} elapsed={elapsed:.1f}s eta={remaining:.1f}s"
            )

    scores = np.array([g["final_score"] for g in per_game], dtype=np.float64)
    max_tiles = np.array([g["max_tile"] for g in per_game], dtype=np.float64)
    invalid_rates = np.array([g["invalid_rate"] for g in per_game], dtype=np.float64)
    durations = np.array([g["duration_ms"] for g in per_game], dtype=np.float64)

    summary = _summary_stats(scores, max_tiles, invalid_rates, durations)
    _print_summary(args.agent, summary, args.quiet)

    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["seed", "final_score", "max_tile", "steps", "invalid_rate", "duration_ms", "moved_steps"],
        )
        writer.writeheader()
        for game in per_game:
            writer.writerow(
                {
                    "seed": game["seed"],
                    "final_score": game["final_score"],
                    "max_tile": game["max_tile"],
                    "steps": game["steps"],
                    "invalid_rate": f"{game['invalid_rate']:.6f}",
                    "duration_ms": f"{game['duration_ms']:.3f}",
                    "moved_steps": game["moved_steps"],
                }
            )

    payload = {
        "config": {
            "agent": args.agent,
            "depth": args.depth,
            "max_cells": args.max_cells,
            "model": args.model if args.agent == "policy" else None,
            "seeds": seeds,
            "max_steps": args.max_steps,
        },
        "summary": summary,
        "per_game": per_game,
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if not args.quiet:
        print(f"saved json: {out_json}")
        print(f"saved csv: {out_csv}")


if __name__ == "__main__":
    main()
