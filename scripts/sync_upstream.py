#!/usr/bin/env python3
"""Sync upstream Mozc and merge-ut-dictionaries SHAs and create release tags."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO_ROOT / "upstream.lock"
GITHUB_API = "https://api.github.com"


def parse_lock(content: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def write_lock(values: dict[str, str]) -> None:
    lines = [
        "# Pinned upstream commit SHAs for reproducible builds.",
        "# Updated automatically by scripts/sync_upstream.py on monthly sync.",
        f"mozc={values['mozc']}",
        f"merge_ut={values['merge_ut']}",
        f"last_release_tag={values.get('last_release_tag', '')}",
        f"last_mozc_sha={values.get('last_mozc_sha', values['mozc'])}",
        f"last_merge_ut_sha={values.get('last_merge_ut_sha', values['merge_ut'])}",
        "",
    ]
    LOCK_FILE.write_text("\n".join(lines), encoding="utf-8")


def fetch_latest_sha(owner: str, repo: str) -> str:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/master"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mozc-ut-privacy-sync",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["sha"]


def fetch_mozc_version(mozc_sha: str) -> tuple[int, int, int]:
    url = (
        "https://raw.githubusercontent.com/google/mozc/"
        f"{mozc_sha}/src/version.bzl"
    )
    with urllib.request.urlopen(url, timeout=60) as response:
        content = response.read().decode("utf-8")

    major = int(re.search(r"^MAJOR = (\d+)", content, re.MULTILINE).group(1))
    minor = int(re.search(r"^MINOR = (\d+)", content, re.MULTILINE).group(1))
    build = int(re.search(r"^BUILD_OSS = (\d+)", content, re.MULTILINE).group(1))
    return major, minor, build


def checkout_submodule(path: Path, sha: str) -> None:
    subprocess.run(["git", "fetch", "origin"], cwd=path, check=True)
    subprocess.run(["git", "checkout", sha], cwd=path, check=True)


def create_tag(tag: str, message: str, push: bool) -> None:
    subprocess.run(["git", "tag", "-a", tag, "-m", message], cwd=REPO_ROOT, check=True)
    if push:
        subprocess.run(["git", "push", "origin", tag], cwd=REPO_ROOT, check=True)


def commit_lock(values: dict[str, str], message: str, push: bool) -> None:
    write_lock(values)
    subprocess.run(["git", "add", str(LOCK_FILE)], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=REPO_ROOT, check=True)
    if push:
        subprocess.run(["git", "push", "origin", "HEAD"], cwd=REPO_ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync upstream SHAs.")
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push commits and tags to origin.",
    )
    parser.add_argument(
        "--force-tag",
        action="store_true",
        help="Create a release tag even if SHAs are unchanged.",
    )
    args = parser.parse_args()

    if not LOCK_FILE.exists():
        print(f"ERROR: Missing lock file: {LOCK_FILE}", file=sys.stderr)
        return 1

    lock = parse_lock(LOCK_FILE.read_text(encoding="utf-8"))
    current_mozc = fetch_latest_sha("google", "mozc")
    current_ut = fetch_latest_sha("utuhiro78", "merge-ut-dictionaries")

    changed = (
        current_mozc != lock.get("mozc")
        or current_ut != lock.get("merge_ut")
    )

    if not changed and not args.force_tag:
        print("No upstream changes detected. Skipping release.")
        return 0

    print(f"Mozc: {lock.get('mozc', 'none')} -> {current_mozc}")
    print(f"merge-ut: {lock.get('merge_ut', 'none')} -> {current_ut}")

    mozc_path = REPO_ROOT / "vendor" / "mozc"
    ut_path = REPO_ROOT / "vendor" / "merge-ut-dictionaries"
    checkout_submodule(mozc_path, current_mozc)
    checkout_submodule(ut_path, current_ut)

    major, minor, build = fetch_mozc_version(current_mozc)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    tag = f"v{major}.{minor}.{build}.{date_str}"

    new_lock = {
        "mozc": current_mozc,
        "merge_ut": current_ut,
        "last_release_tag": tag,
        "last_mozc_sha": lock.get("mozc", current_mozc),
        "last_merge_ut_sha": lock.get("merge_ut", current_ut),
    }

    commit_lock(
        new_lock,
        f"Sync upstream to Mozc {current_mozc[:8]}, merge-ut {current_ut[:8]}",
        push=args.push,
    )
    create_tag(tag, f"Release {tag}", push=args.push)
    print(f"Created release tag: {tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
