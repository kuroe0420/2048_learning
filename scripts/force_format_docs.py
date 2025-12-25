from __future__ import annotations

from pathlib import Path
import re
import sys

TARGETS = [
    ("PROGRESS", Path("docs/PROGRESS.md")),
    ("SPEC", Path("docs/imitation_learning_spec.md")),
]


def _insert_line_breaks(text: str) -> str:
    # Insert line breaks before headings and list items when missing (non-start).
    for pattern in ["### ", "## ", "# "]:
        text = re.sub(rf"(?<!\n)({re.escape(pattern)})", r"\n\1", text)
    text = re.sub(r"(?<!\n)(- )", r"\n\1", text)

    # Code fences should be on their own lines.
    text = re.sub(r"(?<!\n)```", r"\n```", text)
    text = re.sub(r"```(?!\n)", r"```\n", text)

    # Ensure a blank line before headings for readability.
    text = re.sub(r"(?<!\n)\n(#{1,6} )", r"\n\n\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    if text.startswith("\n"):
        text = text[1:]
    return text


def process(label: str, path: Path) -> int:
    before_bytes = path.read_bytes()
    bom_removed = False
    if before_bytes[:3] == b"\xef\xbb\xbf":
        before_bytes = before_bytes[3:]
        bom_removed = True

    text = before_bytes.decode("utf-8", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    before_lines = text.count("\n") + 1
    if before_lines == 1:
        text = _insert_line_breaks(text)

    after_lines = text.count("\n") + 1
    path.write_text(text, encoding="utf-8", newline="\n")

    print(f"{label}: before_lines={before_lines} after_lines={after_lines} bom_removed={bom_removed}")

    return 0 if after_lines > 1 else 1


def main() -> int:
    exit_code = 0
    for label, path in TARGETS:
        if not path.exists():
            print(f"{label}: missing {path}", file=sys.stderr)
            exit_code = 1
            continue
        exit_code = max(exit_code, process(label, path))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
