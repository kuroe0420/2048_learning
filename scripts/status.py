import subprocess
from pathlib import Path


def _run_git(args):
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _extract_updated(progress_path: Path) -> str:
    if not progress_path.exists():
        return "unknown"
    for line in progress_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip().lstrip("\ufeff")
        if stripped.startswith("最終更新:"):
            return stripped.replace("最終更新:", "").strip() or "unknown"
    return "unknown"


def _extract_section_first_line(progress_text: str, heading: str) -> str:
    lines = progress_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lstrip("\ufeff") == heading:
            for next_line in lines[i + 1 :]:
                stripped = next_line.strip()
                if not stripped:
                    continue
                if stripped.startswith("##"):
                    break
                return stripped
    return "unknown"


def _read_tests(artifact_path: Path) -> str:
    if not artifact_path.exists():
        return "unknown"
    lines = artifact_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return "unknown"
    return lines[0].strip() or "unknown"


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    progress_path = repo_root / "docs" / "PROGRESS.md"
    progress_text = progress_path.read_text(encoding="utf-8") if progress_path.exists() else ""
    updated = _extract_updated(progress_path)

    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    commit_hash = _run_git(["rev-parse", "--short", "HEAD"])
    commit_msg = _run_git(["log", "-1", "--pretty=%s"])
    commit = f"{commit_hash} {commit_msg}" if commit_hash != "unknown" else "unknown"

    tests = _read_tests(repo_root / ".artifacts" / "pytest_last.txt")
    next_line = _extract_section_first_line(progress_text, "## 次にやること")
    blockers = _extract_section_first_line(progress_text, "## ブロッカー")

    print("# PROGRESS_UPDATE")
    print(f"updated: {updated}")
    print(f"branch: {branch}")
    print(f"commit: {commit}")
    print(f"tests: {tests}")
    print(f"next: {next_line}")
    print(f"blockers: {blockers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
