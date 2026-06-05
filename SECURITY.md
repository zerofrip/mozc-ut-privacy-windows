# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Open a [GitHub Security Advisory](https://github.com/mozc-ut-privacy/mozc-ut-privacy-windows/security/advisories/new) or contact the maintainers privately.
3. Include steps to reproduce, affected versions, and potential impact.

We aim to acknowledge reports within 7 days.

## Threat Model

### In Scope

- Supply chain integrity (upstream lock file, release checksums)
- Updater download and install security
- Code signing verification
- Unauthorized network access from the IME

### Out of Scope

- Vulnerabilities in upstream Mozc (report to [google/mozc](https://github.com/google/mozc))
- Vulnerabilities in upstream merge-ut-dictionaries
- Social engineering attacks

## Privacy Audit Checklist

The IME must pass all checks:

- [ ] `mozc_server.exe` makes no outbound network connections
- [ ] `mozc_broker.exe` makes no outbound network connections
- [ ] `mozc_tip*.dll` makes no outbound network connections
- [ ] No Omaha / Google Update integration (OSS `MOZC_BUILD` stubs only)
- [ ] No crash reporting or analytics endpoints
- [ ] Updater is a separate binary, not embedded in the IME process

## Updater Security

The updater (`MozcUTUpdater.exe`) is the only component that makes network requests:

| Control | Implementation |
|---------|----------------|
| TLS | WinHTTP with `WINHTTP_FLAG_SECURE` |
| Host restriction | Only `api.github.com` and `github.com` |
| Integrity | SHA256 verification against `SHA256SUMS.txt` (mandatory) |
| Rollback | Previous MSI backed up to `%ProgramData%\MozcUTPrivacy\versions\previous\` |
| User consent | Default `install_mode: prompt` |
| No telemetry | No data sent beyond HTTP GET requests |

See [docs/NETWORK.md](docs/NETWORK.md) for the complete network request inventory.

## Supply Chain

- Upstream SHAs pinned in `upstream.lock`
- Patches are reviewed and version-controlled
- Release artifacts include `SHA256SUMS.txt`
- Optional Authenticode signing when credentials are configured
- License compliance verified by `scripts/generate_licenses.py --check` in CI

## Code Signing

When `WINDOWS_CODE_SIGNING_CERT_BASE64` is configured, all MSI and updater binaries are signed with `signtool` and timestamped. Users should verify signatures before installing.
