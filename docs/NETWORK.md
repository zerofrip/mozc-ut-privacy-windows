# Network Request Inventory

This document lists **every network request** made by Mozc UT Privacy Edition components. The IME itself makes no network requests.

## Runtime Components

### IME (mozc_server, mozc_broker, mozc_tip, mozc_tool, mozc_renderer)

| Attribute | Value |
|-----------|-------|
| Network requests | **None** |
| Telemetry | **None** |
| Analytics | **None** |
| Cloud conversion | **None** |

All Japanese input conversion is performed locally using the embedded `mozc.data` dictionary.

### Updater (MozcUTUpdater.exe)

The updater is optional and runs separately from the IME (typically via a Windows Scheduled Task).

#### Request 1: Check for updates

| Attribute | Value |
|-----------|-------|
| When | Scheduled task (default: daily at 03:00) or `--check-now` |
| Method | `GET` |
| URL | `https://api.github.com/repos/{owner}/{repo}/releases/latest` |
| Default owner/repo | `mozc-ut-privacy/mozc-ut-privacy-windows` |
| Data sent | `User-Agent: MozcUTUpdater/1.0` header only |
| Data received | Public GitHub Release metadata (JSON): tag name, asset URLs |
| Purpose | Determine if a newer version is available |

#### Request 2: Download checksums

| Attribute | Value |
|-----------|-------|
| When | Only when an update is available and user confirms (or silent mode) |
| Method | `GET` |
| URL | `https://github.com/{owner}/{repo}/releases/download/{tag}/SHA256SUMS.txt` |
| Data sent | `User-Agent: MozcUTUpdater/1.0` header only |
| Data received | SHA256 checksum file |
| Purpose | Verify download integrity before installation |

#### Request 3: Download MSI installer

| Attribute | Value |
|-----------|-------|
| When | Only when an update is available, checksums verified |
| Method | `GET` |
| URL | `https://github.com/{owner}/{repo}/releases/download/{tag}/MozcUTPrivacy-{ver}-win-{arch}.msi` |
| Data sent | `User-Agent: MozcUTUpdater/1.0` header only |
| Data received | MSI installer binary |
| Purpose | Install the updated version |

#### Updater guarantees

- TLS 1.2+ (WinHTTP `WINHTTP_FLAG_SECURE`)
- Only contacts `api.github.com` and `github.com`
- SHA256 verification is **mandatory** before install
- No usage data, crash reports, or analytics sent
- Failed installs trigger rollback from local backup

## Build-Time Only (CI / Local Build)

These requests occur during dictionary generation and are **not present** in the installed IME.

### Dictionary source repositories

| URL | Purpose |
|-----|---------|
| `https://github.com/utuhiro78/mozcdic-ut-jawiki.git` | Pre-built jawiki dictionary |
| `https://github.com/utuhiro78/mozcdic-ut-sudachidict.git` | Pre-built SudachiDict entries |
| `https://github.com/utuhiro78/mozcdic-ut-personal-names.git` | Personal names dictionary |
| `https://github.com/utuhiro78/mozcdic-ut-place-names.git` | Place names dictionary |

### Japanese Wikipedia title index

| URL | Purpose |
|-----|---------|
| `https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles-multistream-index.txt.bz2-rss.xml` | Discover latest index URL |
| `https://dumps.wikimedia.org/.../jawiki-latest-pages-articles-multistream-index.txt.bz2` | Download title index for cost tuning |

License: [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)

### Upstream sync (monthly CI)

| URL | Purpose |
|-----|---------|
| `https://api.github.com/repos/google/mozc/commits/master` | Latest Mozc SHA |
| `https://api.github.com/repos/utuhiro78/merge-ut-dictionaries/commits/master` | Latest merge-ut SHA |
| `https://raw.githubusercontent.com/google/mozc/{sha}/src/version.bzl` | Parse Mozc version for tagging |

### Mozc build dependencies

| Source | Purpose |
|--------|---------|
| `update_deps.py` URLs | Qt, LLVM, MSYS2, Ninja (see Mozc docs) |
| Bazel module fetches | Abseil, Protobuf, etc. (see `MODULE.bazel`) |

## Configuration

Updater behavior is controlled by `%ProgramData%\MozcUTPrivacy\updater.json`:

```json
{
  "github_owner": "mozc-ut-privacy",
  "github_repo": "mozc-ut-privacy-windows",
  "check_interval_hours": 24,
  "install_mode": "prompt",
  "allow_prerelease": false
}
```

To disable the updater entirely, do not register the scheduled task (see `updater/powershell/Install-UpdaterTask.ps1`).
