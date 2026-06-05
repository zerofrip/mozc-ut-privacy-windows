#pragma once

#include <string>
#include <vector>

namespace mozc_ut {

struct ReleaseAsset {
  std::string name;
  std::string download_url;
  std::string browser_download_url;
};

struct ReleaseInfo {
  std::string tag_name;
  std::string body;
  std::vector<ReleaseAsset> assets;
};

bool HttpGet(const std::wstring& host, const std::wstring& path,
             std::string* response);
bool FetchLatestRelease(const std::string& owner, const std::string& repo,
                        ReleaseInfo* release);
bool DownloadFile(const std::string& url, const std::wstring& output_path);
std::string ExtractJsonStringValue(const std::string& json,
                                   const std::string& key);
ReleaseAsset FindMsiAsset(const ReleaseInfo& release,
                          const std::wstring& architecture);
ReleaseAsset FindChecksumAsset(const ReleaseInfo& release);

}  // namespace mozc_ut
