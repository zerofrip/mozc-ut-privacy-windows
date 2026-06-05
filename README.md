# Mozc UT Privacy Edition (Windows)

An unofficial, privacy-focused Windows distribution of [Mozc](https://github.com/google/mozc) with [merge-ut-dictionaries](https://github.com/utuhiro78/merge-ut-dictionaries) integrated.

## Features

- **Expanded dictionary** — Community UT dictionaries merged automatically during each build
- **No telemetry** — No analytics, tracking, or cloud conversion services
- **Local processing** — All IME conversion happens on your machine
- **Optional updater** — Separate updater checks GitHub Releases only (see [docs/NETWORK.md](docs/NETWORK.md))
- **Full license compliance** — `LICENSES.txt`, `THIRD_PARTY_LICENSES.txt`, and `CREDITS.txt` bundled in every release

## Downloads

Releases are published on the [GitHub Releases](https://github.com/mozc-ut-privacy/mozc-ut-privacy-windows/releases) page.

Each release includes:

| Artifact | Description |
|----------|-------------|
| `MozcUTPrivacy-{ver}-win-x64.msi` | x64 installer |
| `MozcUTPrivacy-{ver}-win-arm64.msi` | ARM64 installer |
| `MozcUTPrivacy-{ver}-win-{arch}-portable.zip` | Portable package |
| `SHA256SUMS.txt` | Checksums for all binaries |
| `MozcUTUpdater-{ver}-win-{arch}.exe` | Optional auto-updater |

## Quick Install

1. Download the MSI matching your architecture (x64 or ARM64).
2. Verify the SHA256 checksum against `SHA256SUMS.txt`.
3. Run the installer with administrator privileges.
4. Add **Japanese** input language in Windows Settings if not already present.
5. Select **Mozc UT Privacy Edition** as the input method.

### Installer exits at "必要な情報を集めています"

| Cause | What to do |
|-------|------------|
| **Wrong architecture** | ARM64 PC (Snapdragon など) では `*-win-arm64.msi` を使用。`x64.msi` は ARM64 ではインストールできません。 |
| **Not elevated** | 右クリック → **管理者として実行**。 |
| **Already installed** | 同じかより新しいバージョンが入っている場合は終了します。設定 → アプリから既存版を確認してください。 |
| **Need details** | PowerShell でログ取得: `msiexec /i "path\to\installer.msi" /l*v "$env:TEMP\mozc-ut-install.log"` |

## Privacy Guarantees

| Component | Network access |
|-----------|----------------|
| IME (mozc_server, mozc_tip, etc.) | **None** |
| Updater (optional) | GitHub Releases API only |
| Build pipeline (CI) | Dictionary sources only; not present in installed IME |

See [SECURITY.md](SECURITY.md) and [docs/NETWORK.md](docs/NETWORK.md) for the complete network audit.

## Repository Structure

```
mozc-ut-privacy-windows/
├── vendor/                  # Git submodules (Mozc + merge-ut-dictionaries)
├── patches/                 # Minimal upstream patches
├── scripts/                 # Build, sync, license, and release automation
├── updater/                 # Standalone C++ updater
├── licenses/                # License manifest and full license texts
├── .github/workflows/       # CI/CD and monthly upstream sync
└── docs/                    # Architecture and network documentation
```

## Building Locally

See [BUILD.md](BUILD.md) for full instructions.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

This is an **unofficial** community project. It is not affiliated with, endorsed by, or maintained by Google LLC. "Mozc" is used descriptively to identify compatibility with the Mozc IME engine.

## License

- Project orchestration code: BSD-3-Clause (see [licenses/project/BSD-3-Clause.txt](licenses/project/BSD-3-Clause.txt))
- Mozc engine: BSD-3-Clause ([google/mozc](https://github.com/google/mozc))
- merge-ut-dictionaries: Apache-2.0 ([utuhiro78/merge-ut-dictionaries](https://github.com/utuhiro78/merge-ut-dictionaries))
- Dictionary data: Combined licenses (see [CREDITS.txt](licenses/manifest.yaml))
