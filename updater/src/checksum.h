#pragma once

#include <string>

namespace mozc_ut {

bool ComputeSha256Hex(const std::wstring& file_path, std::string* hex_digest);
bool VerifySha256(const std::wstring& file_path, const std::string& expected_hex);
bool VerifyChecksumFile(const std::wstring& checksum_file,
                        const std::wstring& target_file,
                        const std::wstring& expected_name);

}  // namespace mozc_ut
