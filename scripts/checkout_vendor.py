#!/usr/bin/env python3
"""Checkout vendored submodules to SHAs pinned in upstream.lock."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO_ROOT / "upstream.lock"


def parse_lock() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in LOCK_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def sync_submodule(path: Path, sha: str) -> None:
    subprocess.run(
        ["git", "submodule", "update", "--init", "--recursive", str(path)],
        cwd=REPO_ROOT,
        check=True,
    )
    subprocess.run(["git", "fetch", "origin"], cwd=path, check=True)
    subprocess.run(["git", "checkout", sha], cwd=path, check=True)


def main() -> int:
    if not LOCK_FILE.exists():
        print(f"ERROR: {LOCK_FILE} not found", file=sys.stderr)
        return 1

    lock = parse_lock()
    sync_submodule(REPO_ROOT / "vendor" / "mozc", lock["mozc"])
    sync_submodule(REPO_ROOT / "vendor" / "merge-ut-dictionaries", lock["merge_ut"])
    print("Vendor submodules checked out to pinned SHAs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
