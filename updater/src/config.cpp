#include "config.h"

#include "util.h"

#include <fstream>
#include <regex>

namespace mozc_ut {

namespace {

std::wstring ConfigPath() {
  return JoinPath(GetProgramDataDir(), L"updater.json");
}

std::wstring VersionPath() {
  return JoinPath(GetProgramDataDir(), L"installed_version.txt");
}

std::string ExtractJsonString(const std::string& json, const std::string& key) {
  const std::regex pattern("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"");
  std::smatch match;
  if (std::regex_search(json, match, pattern) && match.size() > 1) {
    return match[1].str();
  }
  return "";
}

int ExtractJsonInt(const std::string& json, const std::string& key) {
  const std::regex pattern("\"" + key + "\"\\s*:\\s*(\\d+)");
  std::smatch match;
  if (std::regex_search(json, match, pattern) && match.size() > 1) {
    return std::stoi(match[1].str());
  }
  return 0;
}

bool ExtractJsonBool(const std::string& json, const std::string& key) {
  const std::regex pattern("\"" + key + "\"\\s*:\\s*(true|false)");
  std::smatch match;
  if (std::regex_search(json, match, pattern) && match.size() > 1) {
    return match[1].str() == "true";
  }
  return false;
}

}  // namespace

bool LoadConfig(UpdaterConfig* config) {
  if (config == nullptr) {
    return false;
  }

  EnsureDirectory(GetProgramDataDir());
  std::ifstream input(WideToUtf8(ConfigPath()));
  if (!input) {
    return true;
  }

  std::string json((std::istreambuf_iterator<char>(input)),
                   std::istreambuf_iterator<char>());

  const std::string owner = ExtractJsonString(json, "github_owner");
  const std::string repo = ExtractJsonString(json, "github_repo");
  const std::string install_mode = ExtractJsonString(json, "install_mode");
  const int interval = ExtractJsonInt(json, "check_interval_hours");

  if (!owner.empty()) {
    config->github_owner = owner;
  }
  if (!repo.empty()) {
    config->github_repo = repo;
  }
  if (!install_mode.empty()) {
    config->install_mode = install_mode;
  }
  if (interval > 0) {
    config->check_interval_hours = interval;
  }
  config->allow_prerelease = ExtractJsonBool(json, "allow_prerelease");
  return true;
}

bool SaveInstalledVersion(const std::string& version) {
  EnsureDirectory(GetProgramDataDir());
  std::ofstream output(WideToUtf8(VersionPath()));
  if (!output) {
    return false;
  }
  output << version;
  return true;
}

bool LoadInstalledVersion(std::string* version) {
  if (version == nullptr) {
    return false;
  }
  std::ifstream input(WideToUtf8(VersionPath()));
  if (!input) {
    return false;
  }
  *version = std::string((std::istreambuf_iterator<char>(input)),
                         std::istreambuf_iterator<char>());
  return !version->empty();
}

}  // namespace mozc_ut
