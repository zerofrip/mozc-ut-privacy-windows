#pragma once

#include <string>
#include <vector>

namespace mozc_ut {

std::wstring Utf8ToWide(const std::string& input);
std::string WideToUtf8(const std::wstring& input);
std::wstring GetProgramDataDir();
std::wstring GetArchitectureSuffix();
bool EnsureDirectory(const std::wstring& path);
std::wstring JoinPath(const std::wstring& left, const std::wstring& right);
std::vector<std::wstring> SplitLines(const std::string& text);
int CompareVersions(const std::string& left, const std::string& right);

}  // namespace mozc_ut
