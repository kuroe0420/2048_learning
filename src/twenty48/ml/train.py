from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import torch
from torch import nn
from torch.utils.data import DataLoader

from .dataset import Twenty48ImitationDataset, split_dataset
from .model import PolicyNet


def train_policy(
    dataset_path: str,
    out_dir: str,
    batch_size: int = 256,
    epochs: int = 10,
    lr: float = 1e-3,
    val_ratio: float = 0.1,
    max_pow: int = 15,
    seed: int | None = None,
    device: str = "auto",
    log_file: str | None = None,
    metrics_csv: str | None = None,
    run_info: Dict[str, str] | None = None,
) -> Tuple[Path, Dict[str, float]]:
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device)
    if seed is not None:
        torch.manual_seed(int(seed))

    dataset = Twenty48ImitationDataset(dataset_path, max_pow=max_pow)
    train_set, val_set = split_dataset(dataset, val_ratio=val_ratio, seed=seed)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=False)

    model = PolicyNet(in_channels=max_pow + 1).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    criterion = nn.CrossEntropyLoss()

    best_val = float("inf")
    best_val_acc = 0.0
    best_path = Path(out_dir) / "policy_best.pt"
    meta_path = Path(out_dir) / "policy_meta.json"
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "train_policy log",
            f"dataset={dataset_path}",
            f"epochs={epochs} batch_size={batch_size} lr={lr} val_ratio={val_ratio}",
            f"max_pow={max_pow} seed={seed} device={device}",
        ]
        if run_info:
            for key, value in run_info.items():
                lines.append(f"{key}={value}")
        log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if metrics_csv:
        csv_path = Path(metrics_csv)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        if not csv_path.exists():
            csv_path.write_text("epoch,train_loss,val_loss,val_acc\n", encoding="utf-8")

    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        for x, y in train_loader:
            x = x.to(device)
            y = y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()
            train_loss += float(loss.item()) * x.size(0)

        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for x, y in val_loader:
                x = x.to(device)
                y = y.to(device)
                logits = model(x)
                loss = criterion(logits, y)
                val_loss += float(loss.item()) * x.size(0)
                preds = torch.argmax(logits, dim=1)
                correct += int((preds == y).sum().item())
                total += int(y.size(0))

        train_loss /= max(1, len(train_set))
        val_loss /= max(1, len(val_set))
        val_acc = correct / max(1, total)

        if val_loss < best_val:
            best_val = val_loss
            best_val_acc = val_acc
            torch.save(model.state_dict(), best_path)
            meta = {
                "in_channels": max_pow + 1,
                "max_pow": max_pow,
                "encoding": "one_hot",
            }
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

        if metrics_csv:
            with Path(metrics_csv).open("a", encoding="utf-8") as handle:
                handle.write(f"{epoch},{train_loss:.6f},{val_loss:.6f},{val_acc:.6f}\n")

        print(
            f"Epoch {epoch}/{epochs} | train_loss={train_loss:.4f} | "
            f"val_loss={val_loss:.4f} | val_acc={val_acc:.4f}"
        )

    if log_file:
        with Path(log_file).open("a", encoding="utf-8") as handle:
            handle.write(
                "final: "
                f"train_loss={train_loss:.6f} val_loss={val_loss:.6f} val_acc={val_acc:.6f}\n"
            )
            handle.write(
                "best: "
                f"val_loss={best_val:.6f} val_acc={best_val_acc:.6f}\n"
            )

    metrics = {"best_val_loss": best_val, "best_val_acc": best_val_acc}
    return best_path, metrics
