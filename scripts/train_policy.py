import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from twenty48.ml.train import train_policy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--out-dir", type=str, default="data/models")
    parser.add_argument("--max-pow", type=int, default=15)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--device", type=str, default="auto", help="auto|cpu|cuda")
    parser.add_argument("--log-file", type=str, default=".artifacts/train_last.log")
    parser.add_argument("--metrics-csv", type=str, default=".artifacts/train_metrics.csv")
    args = parser.parse_args()

    train_policy(
        dataset_path=args.dataset,
        out_dir=args.out_dir,
        batch_size=args.batch_size,
        epochs=args.epochs,
        lr=args.lr,
        val_ratio=args.val_ratio,
        max_pow=args.max_pow,
        seed=args.seed,
        device=args.device,
        log_file=args.log_file,
        metrics_csv=args.metrics_csv,
        run_info={"command": " ".join(sys.argv)},
    )


if __name__ == "__main__":
    main()
