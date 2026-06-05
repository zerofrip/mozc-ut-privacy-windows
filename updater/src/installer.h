#pragma once

#include <string>

namespace mozc_ut {

bool BackupCurrentInstall(const std::wstring& msi_path);
bool InstallMsi(const std::wstring& msi_path, bool silent);
bool RollbackInstall();

}  // namespace mozc_ut
