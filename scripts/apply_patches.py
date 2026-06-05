#!/usr/bin/env python3
"""Apply ordered patches to vendored upstream sources."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PATCH_DIRS = [
    REPO_ROOT / "patches" / "mozc",
    REPO_ROOT / "patches" / "merge-ut",
]

# Keep LF line endings so patches apply consistently on Windows CI runners.
GIT_APPLY_PREFIX = ["git", "-c", "core.autocrlf=false", "-c", "core.eol=lf"]
GIT_APPLY_FLAGS = ["--whitespace=nowarn"]


def git_apply(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        GIT_APPLY_PREFIX + ["apply"] + GIT_APPLY_FLAGS + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def apply_patch(patch_file: Path) -> None:
    if patch_file.parent.name == "mozc":
        cwd = REPO_ROOT / "vendor" / "mozc"
    elif patch_file.parent.name == "merge-ut":
        cwd = REPO_ROOT / "vendor" / "merge-ut-dictionaries"
    else:
        raise RuntimeError(f"Unknown patch directory for {patch_file}")

    if not cwd.exists():
        raise RuntimeError(f"Vendor directory not found: {cwd}")

    print(f"Applying {patch_file.name} in {cwd}")
    result = git_apply(["--check", str(patch_file)], cwd)
    if result.returncode != 0:
        result = git_apply(["--reverse", "--check", str(patch_file)], cwd)
        if result.returncode == 0:
            print("  Already applied, skipping.")
            return
        raise RuntimeError(
            f"Patch check failed for {patch_file}:\n{result.stderr}"
        )

    result = git_apply([str(patch_file)], cwd)
    if result.returncode != 0:
        raise RuntimeError(
            f"Patch apply failed for {patch_file}:\n{result.stderr}"
        )


def main() -> int:
    for patch_dir in PATCH_DIRS:
        if not patch_dir.exists():
            continue
        for patch_file in sorted(patch_dir.glob("*.patch")):
            apply_patch(patch_file)
    print("All patches applied successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
