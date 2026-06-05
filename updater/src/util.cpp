#include "util.h"

#include <windows.h>
#include <shlwapi.h>

#include <algorithm>
#include <sstream>

namespace mozc_ut {

std::wstring Utf8ToWide(const std::string& input) {
  if (input.empty()) {
    return L"";
  }
  const int size = MultiByteToWideChar(
      CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), nullptr, 0);
  std::wstring output(size, L'\0');
  MultiByteToWideChar(
      CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), output.data(),
      size);
  return output;
}

std::string WideToUtf8(const std::wstring& input) {
  if (input.empty()) {
    return "";
  }
  const int size = WideCharToMultiByte(
      CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), nullptr, 0,
      nullptr, nullptr);
  std::string output(size, '\0');
  WideCharToMultiByte(
      CP_UTF8, 0, input.c_str(), static_cast<int>(input.size()), output.data(),
      size, nullptr, nullptr);
  return output;
}

std::wstring GetProgramDataDir() {
  wchar_t buffer[MAX_PATH] = {};
  ExpandEnvironmentStringsW(L"%ProgramData%\\MozcUTPrivacy", buffer, MAX_PATH);
  return buffer;
}

std::wstring GetArchitectureSuffix() {
  SYSTEM_INFO info = {};
  GetNativeSystemInfo(&info);
  if (info.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_ARM64) {
    return L"arm64";
  }
  return L"x64";
}

bool EnsureDirectory(const std::wstring& path) {
  return SHCreateDirectoryExW(nullptr, path.c_str(), nullptr) == ERROR_SUCCESS ||
         GetLastError() == ERROR_ALREADY_EXISTS;
}

std::wstring JoinPath(const std::wstring& left, const std::wstring& right) {
  wchar_t buffer[MAX_PATH] = {};
  PathCombineW(buffer, left.c_str(), right.c_str());
  return buffer;
}

std::vector<std::wstring> SplitLines(const std::string& text) {
  std::vector<std::wstring> lines;
  std::istringstream stream(text);
  std::string line;
  while (std::getline(stream, line)) {
    if (!line.empty() && line.back() == '\r') {
      line.pop_back();
    }
    lines.push_back(Utf8ToWide(line));
  }
  return lines;
}

int CompareVersions(const std::string& left, const std::string& right) {
  auto parse = [](const std::string& value) {
    std::vector<int> parts;
    std::istringstream stream(value);
    std::string token;
    while (std::getline(stream, token, '.')) {
      parts.push_back(std::stoi(token));
    }
    return parts;
  };

  const auto left_parts = parse(left);
  const auto right_parts = parse(right);
  const size_t count = std::max(left_parts.size(), right_parts.size());
  for (size_t i = 0; i < count; ++i) {
    const int l = i < left_parts.size() ? left_parts[i] : 0;
    const int r = i < right_parts.size() ? right_parts[i] : 0;
    if (l < r) {
      return -1;
    }
    if (l > r) {
      return 1;
    }
  }
  return 0;
}

}  // namespace mozc_ut
