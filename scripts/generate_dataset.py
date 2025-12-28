import argparse
import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from twenty48.env import Twenty48Env
from twenty48.ai.expectimax import choose_action


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-games", type=int, default=200)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--out", type=str, default=None)
    parser.add_argument("--sample-prob", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--include-invalid", action="store_true")
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--max-cells", type=int, default=4)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--log-file", type=str, default=".artifacts/generate_dataset_last.log")
    args = parser.parse_args()

    out_path = Path(args.out) if args.out else Path("data/raw") / f"dataset_expectimax_depth{args.depth}_games{args.num_games}.npz"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)

    boards = []
    actions = []
    scores = []
    rewards = []
    max_tiles = []
    dones = []
    step_indices = []
    seeds = []
    depths = []

    env = Twenty48Env()

    total_steps = 0
    total_samples = 0
    start_time = time.perf_counter()
    progress_every = max(1, int(args.progress_every))

    for game_idx in range(args.num_games):
        game_seed = args.seed + game_idx if args.seed is not None else None
        env.reset(seed=game_seed)
        done = False
        step = 0
        game_steps = 0
        game_samples = 0
        while not done:
            action = choose_action(env, args.depth, max_cells=args.max_cells)
            board_before = env.board.copy()
            _, reward, done, info = env.step(action)

            if info["invalid_move"] and not args.include_invalid:
                step += 1
                continue

            if rng.random() <= args.sample_prob:
                boards.append(board_before.astype(np.int16))
                actions.append(action)
                scores.append(info["score"])
                rewards.append(reward)
                max_tiles.append(info["max_tile"])
                dones.append(done)
                step_indices.append(step)
                seeds.append(-1 if game_seed is None else int(game_seed))
                depths.append(args.depth)
                game_samples += 1

            step += 1
            game_steps += 1
            if args.max_steps is not None and step >= args.max_steps:
                break

        total_steps += game_steps
        total_samples += game_samples
        if not args.quiet and (
            (game_idx + 1) % progress_every == 0
            or game_idx == 0
            or (game_idx + 1) == args.num_games
        ):
            elapsed = time.perf_counter() - start_time
            avg_per_game = elapsed / (game_idx + 1)
            remaining = max(0, args.num_games - (game_idx + 1))
            eta = avg_per_game * remaining
            print(
                f"[{game_idx + 1}/{args.num_games}] steps={total_steps} "
                f"samples={total_samples} elapsed={elapsed:.1f}s eta={eta:.1f}s"
            )

    np.savez_compressed(
        out_path,
        boards=np.asarray(boards, dtype=np.int16),
        actions=np.asarray(actions, dtype=np.uint8),
        scores=np.asarray(scores, dtype=np.int32),
        rewards=np.asarray(rewards, dtype=np.int32),
        max_tiles=np.asarray(max_tiles, dtype=np.int16),
        dones=np.asarray(dones, dtype=np.bool_),
        step_indices=np.asarray(step_indices, dtype=np.int32),
        seeds=np.asarray(seeds, dtype=np.int32),
        depths=np.asarray(depths, dtype=np.int16),
    )
    elapsed = time.perf_counter() - start_time
    if not args.quiet:
        print(
            f"done games={args.num_games} steps={total_steps} samples={total_samples} "
            f"elapsed={elapsed:.1f}s"
        )
    if args.log_file:
        log_path = Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            "\n".join(
                [
                    "generate_dataset log",
                    f"out={out_path}",
                    f"num_games={args.num_games}",
                    f"depth={args.depth}",
                    f"max_cells={args.max_cells}",
                    f"max_steps={args.max_steps}",
                    f"sample_prob={args.sample_prob}",
                    f"seed={args.seed}",
                    f"steps={total_steps}",
                    f"samples={total_samples}",
                    f"elapsed_sec={elapsed:.3f}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
