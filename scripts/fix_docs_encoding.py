from __future__ import annotations

from pathlib import Path
import re
import sys

TARGETS = [
    Path("docs/PROGRESS.md"),
    Path("docs/imitation_learning_spec.md"),
]


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Add newline before headings when missing (avoid splitting ## into #\n#)
    text = re.sub(r"(?<!\n)(?<!#)(#{1,6} )", r"\n\1", text)

    # Add newline before list items when missing
    text = re.sub(r"(?<!\n)(- )", r"\n\1", text)

    # Ensure code fences are on their own lines
    text = re.sub(r"(?<!\n)```", r"\n```", text)
    text = re.sub(r"```(?!\n)", r"```\n", text)

    # Collapse triple newlines to double to avoid excessive gaps
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading newline if we introduced one at the very start
    if text.startswith("\n"):
        text = text[1:]

    return text


def process_file(path: Path) -> int:
    before_bytes = path.read_bytes()
    has_bom = before_bytes[:3] == b"\xef\xbb\xbf"
    if has_bom:
        before_bytes = before_bytes[3:]

    text = before_bytes.decode("utf-8", errors="replace")
    before_lines = text.count("\n") + 1
    before_has_crlf = "\r\n" in text

    normalized = normalize_markdown(text)
    after_lines = normalized.count("\n") + 1

    path.write_text(normalized, encoding="utf-8", newline="\n")

    print(f"{path}: lines {before_lines} -> {after_lines}")
    print(f"{path}: BOM removed {has_bom}")
    print(f"{path}: CRLF->LF {before_has_crlf}")

    if after_lines <= 1:
        print(f"WARNING: {path} still has <= 1 line", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    code = 0
    for path in TARGETS:
        if not path.exists():
            print(f"Missing: {path}", file=sys.stderr)
            code = 1
            continue
        code = max(code, process_file(path))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
