#pragma once

#include <string>

namespace mozc_ut {

struct UpdaterConfig {
  std::string github_owner = "mozc-ut-privacy";
  std::string github_repo = "mozc-ut-privacy-windows";
  int check_interval_hours = 24;
  std::string install_mode = "prompt";  // "prompt" or "silent"
  bool allow_prerelease = false;
};

bool LoadConfig(UpdaterConfig* config);
bool SaveInstalledVersion(const std::string& version);
bool LoadInstalledVersion(std::string* version);

}  // namespace mozc_ut
