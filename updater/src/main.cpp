// Mozc UT Privacy Edition updater.
// Privacy-focused: only contacts GitHub Releases API. No telemetry.

#include "checksum.h"
#include "config.h"
#include "github_client.h"
#include "installer.h"
#include "util.h"

#include <windows.h>

#include <iostream>
#include <string>

namespace {

bool PromptUser(const std::string& message) {
  const int result = MessageBoxW(
      nullptr, mozc_ut::Utf8ToWide(message).c_str(),
      L"Mozc UT Privacy Edition Updater",
      MB_YESNO | MB_ICONINFORMATION);
  return result == IDYES;
}

std::string NormalizeTag(const std::string& tag) {
  if (!tag.empty() && tag[0] == 'v') {
    return tag.substr(1);
  }
  return tag;
}

}  // namespace

int wmain(int argc, wchar_t* argv[]) {
  bool check_now = false;
  bool silent = false;
  for (int i = 1; i < argc; ++i) {
    if (wcscmp(argv[i], L"--check-now") == 0) {
      check_now = true;
    } else if (wcscmp(argv[i], L"--silent") == 0) {
      silent = true;
    }
  }

  mozc_ut::UpdaterConfig config;
  if (!mozc_ut::LoadConfig(&config)) {
    std::wcerr << L"Failed to load updater config.\n";
    return 1;
  }

  mozc_ut::ReleaseInfo release;
  if (!mozc_ut::FetchLatestRelease(config.github_owner, config.github_repo,
                                   &release)) {
    std::wcerr << L"Failed to fetch latest release from GitHub.\n";
    return 1;
  }

  std::string installed;
  mozc_ut::LoadInstalledVersion(&installed);
  const std::string latest = NormalizeTag(release.tag_name);
  if (!installed.empty() &&
      mozc_ut::CompareVersions(installed, latest) >= 0) {
    if (check_now) {
      std::wcout << L"No update available.\n";
    }
    return 0;
  }

  const std::wstring arch = mozc_ut::GetArchitectureSuffix();
  const auto msi_asset = mozc_ut::FindMsiAsset(release, arch);
  if (msi_asset.browser_download_url.empty()) {
    std::wcerr << L"No MSI asset found for this architecture.\n";
    return 1;
  }

  if (!silent && config.install_mode == "prompt") {
    const std::string prompt =
        "A new version (" + release.tag_name +
        ") is available. Install now?";
    if (!PromptUser(prompt)) {
      return 0;
    }
  }

  mozc_ut::EnsureDirectory(mozc_ut::GetProgramDataDir());
  const std::wstring download_dir =
      mozc_ut::JoinPath(mozc_ut::GetProgramDataDir(), L"downloads");
  mozc_ut::EnsureDirectory(download_dir);

  const std::wstring msi_path =
      mozc_ut::JoinPath(download_dir, mozc_ut::Utf8ToWide(msi_asset.name));
  const std::wstring checksum_path =
      mozc_ut::JoinPath(download_dir, L"SHA256SUMS.txt");

  const auto checksum_asset = mozc_ut::FindChecksumAsset(release);
  if (!checksum_asset.browser_download_url.empty()) {
    if (!mozc_ut::DownloadFile(checksum_asset.browser_download_url,
                                checksum_path)) {
      std::wcerr << L"Failed to download checksum file.\n";
      return 1;
    }
  }

  if (!mozc_ut::DownloadFile(msi_asset.browser_download_url, msi_path)) {
    std::wcerr << L"Failed to download MSI.\n";
    return 1;
  }

  if (GetFileAttributesW(checksum_path.c_str()) != INVALID_FILE_ATTRIBUTES) {
    if (!mozc_ut::VerifyChecksumFile(checksum_path, msi_path,
                                     mozc_ut::Utf8ToWide(msi_asset.name))) {
      std::wcerr << L"SHA256 verification failed.\n";
      return 1;
    }
  } else {
    std::wcerr << L"Warning: SHA256SUMS.txt not available; refusing install.\n";
    return 1;
  }

  mozc_ut::BackupCurrentInstall(msi_path);
  if (!mozc_ut::InstallMsi(msi_path, silent || config.install_mode == "silent")) {
    std::wcerr << L"Installation failed; attempting rollback.\n";
    if (!mozc_ut::RollbackInstall()) {
      std::wcerr << L"Rollback failed.\n";
      return 1;
    }
    return 1;
  }

  mozc_ut::SaveInstalledVersion(latest);
  std::wcout << L"Updated to " << mozc_ut::Utf8ToWide(release.tag_name)
             << L"\n";
  return 0;
}
