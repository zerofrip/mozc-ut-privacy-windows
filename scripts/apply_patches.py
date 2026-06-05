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


def apply_patch(patch_file: Path) -> None:
    # Determine target directory from patch path prefix.
    if patch_file.parent.name == "mozc":
        cwd = REPO_ROOT / "vendor" / "mozc"
    elif patch_file.parent.name == "merge-ut":
        cwd = REPO_ROOT / "vendor" / "merge-ut-dictionaries"
    else:
        raise RuntimeError(f"Unknown patch directory for {patch_file}")

    if not cwd.exists():
        raise RuntimeError(f"Vendor directory not found: {cwd}")

    print(f"Applying {patch_file.name} in {cwd}")
    result = subprocess.run(
        ["git", "apply", "--check", str(patch_file)],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Already applied patches are skipped.
        result = subprocess.run(
            ["git", "apply", "--reverse", "--check", str(patch_file)],
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  Already applied, skipping.")
            return
        raise RuntimeError(
            f"Patch check failed for {patch_file}:\n{result.stderr}"
        )

    subprocess.run(
        ["git", "apply", str(patch_file)],
        cwd=cwd,
        check=True,
    )


def main() -> int:
    for patch_dir in PATCH_DIRS:
        if not patch_dir.exists():
            continue
        patches = sorted(patch_dir.glob("*.patch"))
        for patch_file in patches:
            apply_patch(patch_file)
    print("All patches applied successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
