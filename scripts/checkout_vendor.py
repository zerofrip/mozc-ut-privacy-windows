#!/usr/bin/env python3
"""Checkout vendored upstream sources to SHAs pinned in upstream.lock."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO_ROOT / "upstream.lock"

VENDORS = {
    "mozc": {
        "path": REPO_ROOT / "vendor" / "mozc",
        "url": "https://github.com/google/mozc.git",
    },
    "merge_ut": {
        "path": REPO_ROOT / "vendor" / "merge-ut-dictionaries",
        "url": "https://github.com/utuhiro78/merge-ut-dictionaries.git",
    },
}

# Prevent CRLF conversion on Windows runners so git apply works reliably.
GIT_LF_CONFIG = ["-c", "core.autocrlf=false", "-c", "core.eol=lf"]


def parse_lock() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in LOCK_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def run_git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git"] + GIT_LF_CONFIG + args, cwd=cwd, check=True)


def try_submodule_init(path: Path) -> bool:
    rel_path = path.relative_to(REPO_ROOT)
    result = subprocess.run(
        ["git"] + GIT_LF_CONFIG + [
            "submodule", "update", "--init", "--recursive", str(rel_path)
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and is_git_repo(path)


def normalize_repo(path: Path, sha: str) -> None:
    run_git(["config", "core.autocrlf", "false"], path)
    run_git(["config", "core.eol", "lf"], path)
    run_git(["fetch", "origin"], path)
    run_git(["checkout", "--force", sha], path)
    run_git(["reset", "--hard", sha], path)


def clone_or_update(path: Path, url: str, sha: str) -> None:
    if path.exists() and not is_git_repo(path):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
        elif path.is_dir():
            shutil.rmtree(path)

    if not is_git_repo(path):
        if not try_submodule_init(path):
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                shutil.rmtree(path)
            print(f"Cloning {url} -> {path}")
            subprocess.run(
                ["git"] + GIT_LF_CONFIG + ["clone", url, str(path)],
                cwd=REPO_ROOT,
                check=True,
            )

    print(f"Checking out {sha[:12]} in {path.name}")
    normalize_repo(path, sha)


def main() -> int:
    if not LOCK_FILE.exists():
        print(f"ERROR: {LOCK_FILE} not found", file=sys.stderr)
        return 1

    lock = parse_lock()
    for key, info in VENDORS.items():
        sha = lock.get(key)
        if not sha:
            print(f"ERROR: Missing {key} SHA in upstream.lock", file=sys.stderr)
            return 1
        clone_or_update(info["path"], info["url"], sha)

    print("Vendor sources checked out to pinned SHAs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
