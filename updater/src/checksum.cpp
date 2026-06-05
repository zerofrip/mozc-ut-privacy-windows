#include "checksum.h"

#include "util.h"

#include <windows.h>
#include <wincrypt.h>

#include <fstream>
#include <iomanip>
#include <sstream>

namespace mozc_ut {

namespace {

std::string BytesToHex(const BYTE* data, DWORD length) {
  std::ostringstream stream;
  stream << std::hex << std::setfill('0');
  for (DWORD i = 0; i < length; ++i) {
    stream << std::setw(2) << static_cast<int>(data[i]);
  }
  return stream.str();
}

}  // namespace

bool ComputeSha256Hex(const std::wstring& file_path, std::string* hex_digest) {
  HCRYPTPROV provider = 0;
  HCRYPTHASH hash = 0;
  if (!CryptAcquireContextW(&provider, nullptr, nullptr, PROV_RSA_AES,
                            CRYPT_VERIFYCONTEXT)) {
    return false;
  }
  if (!CryptCreateHash(provider, CALG_SHA_256, 0, 0, &hash)) {
    CryptReleaseContext(provider, 0);
    return false;
  }

  std::ifstream input(WideToUtf8(file_path), std::ios::binary);
  if (!input) {
    CryptDestroyHash(hash);
    CryptReleaseContext(provider, 0);
    return false;
  }

  char buffer[8192];
  while (input.read(buffer, sizeof(buffer)) || input.gcount() > 0) {
    if (!CryptHashData(hash, reinterpret_cast<BYTE*>(buffer),
                       static_cast<DWORD>(input.gcount()), 0)) {
      CryptDestroyHash(hash);
      CryptReleaseContext(provider, 0);
      return false;
    }
  }

  BYTE digest[32];
  DWORD digest_len = sizeof(digest);
  if (!CryptGetHashParam(hash, HP_HASHVAL, digest, &digest_len, 0)) {
    CryptDestroyHash(hash);
    CryptReleaseContext(provider, 0);
    return false;
  }

  *hex_digest = BytesToHex(digest, digest_len);
  CryptDestroyHash(hash);
  CryptReleaseContext(provider, 0);
  return true;
}

bool VerifySha256(const std::wstring& file_path,
                  const std::string& expected_hex) {
  std::string actual;
  if (!ComputeSha256Hex(file_path, &actual)) {
    return false;
  }
  return actual == expected_hex;
}

bool VerifyChecksumFile(const std::wstring& checksum_file,
                        const std::wstring& target_file,
                        const std::wstring& expected_name) {
  std::ifstream input(WideToUtf8(checksum_file));
  if (!input) {
    return false;
  }

  const std::string target_name = WideToUtf8(expected_name);
  std::string line;
  while (std::getline(input, line)) {
    if (line.empty()) {
      continue;
    }
    const size_t space_pos = line.find("  ");
    if (space_pos == std::string::npos) {
      continue;
    }
    const std::string hash = line.substr(0, space_pos);
    const std::string name = line.substr(space_pos + 2);
    if (name == target_name) {
      return VerifySha256(target_file, hash);
    }
  }
  return false;
}

}  // namespace mozc_ut
