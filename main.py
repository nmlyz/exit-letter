#!/usr/bin/env python3
"""The One-Line Exit -- submission generator.

Writes a single-line resignation letter to ``entry.txt`` inside the
output directory (``OUTPUT_DIR`` env var, default ``/output``).

The output is deterministic: two runs produce byte-identical files.
"""

import os
import sys
from pathlib import Path

ENTRY_LINE = "I am resigning as a ghostwriter: I have written 14 memoirs in other people's voices, and this is the first sentence that is mine."

MAX_CHARS = 140
ENTRY_NAME = "entry.txt"


class EntryError(ValueError):
    """Raised when the entry line breaks a submission rule."""


def build_payload(line: str) -> bytes:
    """Validate the line and return the exact bytes to write."""
    if not line:
        raise EntryError("entry line must not be empty")
    if len(line) > MAX_CHARS:
        raise EntryError(f"entry line is {len(line)} chars, max is {MAX_CHARS}")
    if any(ch in line for ch in "\r\n"):
        raise EntryError("entry line must be a single line")
    if not line.isascii() or any(ord(ch) < 0x20 for ch in line):
        raise EntryError("entry line must be printable ASCII only")
    if line != line.strip():
        raise EntryError("entry line must not have leading or trailing space")
    if not line.endswith("."):
        raise EntryError("entry line must end with a full stop")
    return (line + "\n").encode("utf-8")


def resolve_output_dir() -> Path:
    """Return the output directory from the environment or the default."""
    raw = os.environ.get("OUTPUT_DIR", "/output")
    directory = Path(raw).expanduser()
    if not directory.is_absolute():
        raise EntryError(f"OUTPUT_DIR must be absolute, got: {raw!r}")
    return directory


def write_entry(directory: Path, payload: bytes) -> Path:
    """Write the payload to entry.txt and confirm what landed on disk."""
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / ENTRY_NAME
    target.write_bytes(payload)
    os.chmod(target, 0o644)
    if target.read_bytes() != payload:
        raise EntryError("written entry.txt does not match the payload")
    return target


def main(argv=None) -> int:
    try:
        payload = build_payload(ENTRY_LINE)
        target = write_entry(resolve_output_dir(), payload)
    except (EntryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {target} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
