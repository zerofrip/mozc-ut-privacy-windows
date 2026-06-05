#include "installer.h"

#include "util.h"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <shellapi.h>

namespace mozc_ut {

namespace {

std::wstring BackupDir() {
  return JoinPath(GetProgramDataDir(), L"versions\\previous");
}

int RunMsiExec(const std::wstring& arguments) {
  SHELLEXECUTEINFOW info = {};
  info.cbSize = sizeof(info);
  info.fMask = SEE_MASK_NOCLOSEPROCESS;
  info.lpVerb = L"open";
  info.lpFile = L"msiexec.exe";
  info.lpParameters = arguments.c_str();
  info.nShow = SW_HIDE;
  if (!ShellExecuteExW(&info) || info.hProcess == nullptr) {
    return -1;
  }
  WaitForSingleObject(info.hProcess, INFINITE);
  DWORD exit_code = 1;
  GetExitCodeProcess(info.hProcess, &exit_code);
  CloseHandle(info.hProcess);
  return static_cast<int>(exit_code);
}

}  // namespace

bool BackupCurrentInstall(const std::wstring& msi_path) {
  EnsureDirectory(JoinPath(GetProgramDataDir(), L"versions"));
  EnsureDirectory(BackupDir());
  const std::wstring backup_msi = JoinPath(BackupDir(), L"previous.msi");
  return CopyFileW(msi_path.c_str(), backup_msi.c_str(), FALSE) != 0;
}

bool InstallMsi(const std::wstring& msi_path, bool silent) {
  std::wstring args = L"/i \"" + msi_path + L"\" /norestart";
  if (silent) {
    args += L" /quiet";
  }
  return RunMsiExec(args) == 0;
}

bool RollbackInstall() {
  const std::wstring backup_msi = JoinPath(BackupDir(), L"previous.msi");
  if (GetFileAttributesW(backup_msi.c_str()) == INVALID_FILE_ATTRIBUTES) {
    return false;
  }
  return InstallMsi(backup_msi, true);
}

}  // namespace mozc_ut
