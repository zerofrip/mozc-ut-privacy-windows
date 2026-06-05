#include "github_client.h"

#include "util.h"

#include <windows.h>
#include <winhttp.h>

#include <fstream>
#include <regex>
#include <vector>

namespace mozc_ut {

namespace {

bool ReadResponse(HINTERNET request, std::string* response) {
  response->clear();
  DWORD available = 0;
  do {
    if (!WinHttpQueryDataAvailable(request, &available)) {
      return false;
    }
    if (available == 0) {
      break;
    }
    std::vector<char> buffer(available);
    DWORD read = 0;
    if (!WinHttpReadData(request, buffer.data(), available, &read)) {
      return false;
    }
    response->append(buffer.data(), read);
  } while (available > 0);
  return true;
}

}  // namespace

bool HttpGet(const std::wstring& host, const std::wstring& path,
             std::string* response) {
  HINTERNET session = WinHttpOpen(L"MozcUTUpdater/1.0",
                                  WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                  WINHTTP_NO_PROXY_NAME,
                                  WINHTTP_NO_PROXY_BYPASS, 0);
  if (!session) {
    return false;
  }

  HINTERNET connection = WinHttpConnect(session, host.c_str(),
                                        INTERNET_DEFAULT_HTTPS_PORT, 0);
  if (!connection) {
    WinHttpCloseHandle(session);
    return false;
  }

  HINTERNET request = WinHttpOpenRequest(
      connection, L"GET", path.c_str(), nullptr, WINHTTP_NO_REFERER,
      WINHTTP_DEFAULT_ACCEPT_TYPES, WINHTTP_FLAG_SECURE);
  if (!request) {
    WinHttpCloseHandle(connection);
    WinHttpCloseHandle(session);
    return false;
  }

  const bool sent = WinHttpSendRequest(request, WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                                       WINHTTP_NO_REQUEST_DATA, 0, 0, 0);
  const bool received = sent && WinHttpReceiveResponse(request, nullptr);
  const bool ok = received && ReadResponse(request, response);

  WinHttpCloseHandle(request);
  WinHttpCloseHandle(connection);
  WinHttpCloseHandle(session);
  return ok;
}

std::string ExtractJsonStringValue(const std::string& json,
                                   const std::string& key) {
  const std::regex pattern("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"");
  std::smatch match;
  if (std::regex_search(json, match, pattern) && match.size() > 1) {
    return match[1].str();
  }
  return "";
}

bool FetchLatestRelease(const std::string& owner, const std::string& repo,
                        ReleaseInfo* release) {
  const std::wstring path =
      L"/repos/" + Utf8ToWide(owner) + L"/" + Utf8ToWide(repo) +
      L"/releases/latest";
  std::string response;
  if (!HttpGet(L"api.github.com", path, &response)) {
    return false;
  }

  release->tag_name = ExtractJsonStringValue(response, "tag_name");
  release->body = ExtractJsonStringValue(response, "body");

  const std::regex asset_pattern(
      R"re("name"\s*:\s*"([^"]*)".*?"browser_download_url"\s*:\s*"([^"]*)")re",
      std::regex::ECMAScript);
  auto begin = std::sregex_iterator(response.begin(), response.end(),
                                    asset_pattern);
  const auto end = std::sregex_iterator();
  for (auto it = begin; it != end; ++it) {
    ReleaseAsset asset;
    asset.name = (*it)[1].str();
    asset.browser_download_url = (*it)[2].str();
    release->assets.push_back(asset);
  }
  return !release->tag_name.empty();
}

bool DownloadFile(const std::string& url, const std::wstring& output_path) {
  const std::wstring wide_url = Utf8ToWide(url);
  const size_t scheme_end = wide_url.find(L"://");
  if (scheme_end == std::wstring::npos) {
    return false;
  }
  const size_t path_start = wide_url.find(L'/', scheme_end + 3);
  if (path_start == std::wstring::npos) {
    return false;
  }

  const std::wstring host =
      wide_url.substr(scheme_end + 3, path_start - scheme_end - 3);
  const std::wstring path = wide_url.substr(path_start);

  HINTERNET session = WinHttpOpen(L"MozcUTUpdater/1.0",
                                  WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                  WINHTTP_NO_PROXY_NAME,
                                  WINHTTP_NO_PROXY_BYPASS, 0);
  if (!session) {
    return false;
  }

  HINTERNET connection = WinHttpConnect(session, host.c_str(),
                                        INTERNET_DEFAULT_HTTPS_PORT, 0);
  if (!connection) {
    WinHttpCloseHandle(session);
    return false;
  }

  HINTERNET request = WinHttpOpenRequest(
      connection, L"GET", path.c_str(), nullptr, WINHTTP_NO_REFERER,
      WINHTTP_DEFAULT_ACCEPT_TYPES, WINHTTP_FLAG_SECURE);
  if (!request) {
    WinHttpCloseHandle(connection);
    WinHttpCloseHandle(session);
    return false;
  }

  bool ok = WinHttpSendRequest(request, WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                               WINHTTP_NO_REQUEST_DATA, 0, 0, 0) &&
            WinHttpReceiveResponse(request, nullptr);

  std::ofstream output(WideToUtf8(output_path), std::ios::binary);
  if (!output) {
    ok = false;
  }

  DWORD available = 0;
  while (ok && WinHttpQueryDataAvailable(request, &available) && available > 0) {
    std::vector<char> buffer(available);
    DWORD read = 0;
    if (!WinHttpReadData(request, buffer.data(), available, &read)) {
      ok = false;
      break;
    }
    output.write(buffer.data(), static_cast<std::streamsize>(read));
  }

  WinHttpCloseHandle(request);
  WinHttpCloseHandle(connection);
  WinHttpCloseHandle(session);
  return ok;
}

ReleaseAsset FindMsiAsset(const ReleaseInfo& release,
                          const std::wstring& architecture) {
  const std::wstring arch = architecture;
  for (const auto& asset : release.assets) {
    const std::wstring name = Utf8ToWide(asset.name);
    if (name.find(L".msi") != std::wstring::npos &&
        name.find(arch) != std::wstring::npos) {
      return asset;
    }
  }
  return {};
}

ReleaseAsset FindChecksumAsset(const ReleaseInfo& release) {
  for (const auto& asset : release.assets) {
    if (asset.name == "SHA256SUMS.txt") {
      return asset;
    }
  }
  return {};
}

}  // namespace mozc_ut
