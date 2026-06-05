#!/usr/bin/env python3
"""Generate GitHub Release notes for a build."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO_ROOT / "upstream.lock"
METADATA_FILE = REPO_ROOT / "generated" / "dictionary_metadata.txt"


def parse_lock() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in LOCK_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def git_log(repo: Path, old_sha: str, new_sha: str) -> list[str]:
    if not old_sha or old_sha == new_sha:
        return ["No changes since last release."]
    result = subprocess.run(
        ["git", "log", "--oneline", f"{old_sha}..{new_sha}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return lines[:30] if lines else ["No commit messages available."]


def read_metadata() -> dict[str, str]:
    if not METADATA_FILE.exists():
        return {}
    values: dict[str, str] = {}
    for line in METADATA_FILE.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release notes.")
    parser.add_argument("--tag", required=True, help="Release tag, e.g. v3.33.6133.20250601")
    parser.add_argument("--output", required=True, help="Output markdown file path.")
    args = parser.parse_args()

    lock = parse_lock()
    metadata = read_metadata()
    build_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    mozc_log = git_log(
        REPO_ROOT / "vendor" / "mozc",
        lock.get("last_mozc_sha", ""),
        lock.get("mozc", ""),
    )
    ut_log = git_log(
        REPO_ROOT / "vendor" / "merge-ut-dictionaries",
        lock.get("last_merge_ut_sha", ""),
        lock.get("merge_ut", ""),
    )

    lines = [
        f"# Mozc UT Privacy Edition {args.tag}",
        "",
        f"**Build date:** {build_date}",
        "",
        "## Privacy",
        "",
        "- No telemetry, analytics, or usage tracking",
        "- No cloud conversion services; all processing is local",
        "- Network access is limited to the optional updater (see SECURITY.md)",
        "",
        "## Upstream Mozc Changes",
        "",
    ]
    lines.extend(f"- {entry}" for entry in mozc_log)
    lines.extend([
        "",
        "## merge-ut-dictionaries Changes",
        "",
    ])
    lines.extend(f"- {entry}" for entry in ut_log)
    lines.extend([
        "",
        "## Dictionary Updates",
        "",
        f"- UT entries integrated: {metadata.get('entry_count', 'unknown')}",
        f"- Enabled sources: {metadata.get('enabled_sources', 'unknown')}",
        "",
        "## Artifacts",
        "",
        "- MSI installer (x64 and ARM64)",
        "- Portable ZIP (x64 and ARM64)",
        "- SHA256SUMS.txt",
        "- MozcUTUpdater binaries",
        "",
    ])

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote release notes to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
