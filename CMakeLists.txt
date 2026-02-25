cmake_minimum_required(VERSION 3.14)
project(ESPx
    VERSION 1.0.0
    DESCRIPTION "ESP32 Wireless Suite - Full C++ Framework"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build options
option(ESPX_BUILD_TESTS "Build unit tests" ON)
option(ESPX_BUILD_EXAMPLES "Build example applications" ON)
option(ESPX_HOST_MODE "Build for host (non-ESP32) testing" ON)

# Compiler warnings
add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
    -Wshadow
    -Wconversion
    -Wsign-conversion
)

if(ESPX_HOST_MODE)
    add_compile_definitions(ESPX_HOST_MODE=1)
endif()

# Collect all source files
file(GLOB_RECURSE ESPX_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
)

# Create the ESPx library
add_library(espx ${ESPX_SOURCES})

target_include_directories(espx
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Platform-specific linking
if(ESPX_HOST_MODE)
    find_package(Threads REQUIRED)
    target_link_libraries(espx PUBLIC Threads::Threads)
endif()

# Tests
if(ESPX_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()

# Examples
if(ESPX_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()
