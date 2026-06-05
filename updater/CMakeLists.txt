cmake_minimum_required(VERSION 3.20)
project(MozcUTUpdater VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(MozcUTUpdater
    src/main.cpp
    src/config.cpp
    src/github_client.cpp
    src/checksum.cpp
    src/installer.cpp
    src/util.cpp
)

target_include_directories(MozcUTUpdater PRIVATE src)
target_link_libraries(MozcUTUpdater PRIVATE winhttp crypt32 shlwapi shell32)

if(MSVC)
    target_compile_definitions(MozcUTUpdater PRIVATE NOMINMAX UNICODE _UNICODE)
    target_compile_options(MozcUTUpdater PRIVATE /W4 /utf-8)
endif()

install(TARGETS MozcUTUpdater RUNTIME DESTINATION bin)
