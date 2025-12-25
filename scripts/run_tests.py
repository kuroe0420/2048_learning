import subprocess
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    artifacts_dir = repo_root / ".artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "pytest_last.txt"

    result = subprocess.run(
        ["python", "-m", "pytest", "-q"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )

    status = "PASS" if result.returncode == 0 else "FAIL"
    output = "\n".join([status, result.stdout.strip(), result.stderr.strip()]).strip() + "\n"
    out_path.write_text(output, encoding="utf-8")

    print(output)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
