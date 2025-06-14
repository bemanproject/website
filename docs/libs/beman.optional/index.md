# beman.optional: C++26 Extensions for std::optional

<!--
SPDX-License-Identifier: 2.0 license with LLVM exceptions
-->


<!-- markdownlint-disable -->
<img src="https://raw.githubusercontent.com/bemanproject/beman/refs/heads/main/images/logos/beman_logo-beman_library_production_ready_api_may_undergo_changes.png" width="5%" height="auto" /> ![CI Tests](https://github.com/bemanproject/optional/actions/workflows/ci.yml/badge.svg) [![Coverage](https://coveralls.io/repos/github/bemanproject/optional/badge.svg?branch=main)](https://coveralls.io/github/bemanproject/optional?branch=main)
<!-- markdownlint-enable -->

This repository implements `std::optional` extensions targeting C++26. The `beman.optional` library aims to evaluate the stability, the usability, and the performance of these proposed changes before they are officially adopted by WG21 into the C++ Working Draft. Additionally, it allows developers to use these new features before they are implemented in major standard library compilers.

**Implements**: [Give *std::optional* Range Support (P3168R2)](https://wg21.link/P3168R2) and [`std::optional<T&>` (P2988R5)](https://wg21.link/P2988R5)

**Status**: [Production ready. API may undergo changes.](../../BEMAN_LIBRARY_MATURITY_MODEL.md#production-ready-api-may-undergo-changes)

## License

Source is licensed with the Apache 2.0 license with LLVM exceptions

// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

Documentation and associated papers are licensed with the Creative Commons Attribution 4.0 International license.

// SPDX-License-Identifier: CC-BY-4.0

The intent is that the source and documentation are available for use by people implementing their own optional types as well as people using the optional presented here as-is.

The README itself is licensed with CC0 1.0 Universal. Copy the contents and incorporate in your own work as you see fit.

// SPDX-License-Identifier: CC0-1.0

## Examples

Full runnable examples can be found in `examples/` - please check [./examples/README.md](https://github.com/bemanproject/optional/blob/main/examples/README.md).

### range_loop

The next code snippet shows optional range support added in [Give *std::optional* Range Support(P3168R2)](https://wg21.link/P3168R2):

```cpp
#include <beman/optional/optional.hpp>
...

beman::optional::optional<int> empty_opt{};
for ([[maybe_unused]] const auto& i : empty_opt) {
    // Should not see this in console.
    std::cout << "\"for each loop\" over C++26 optional: empty_opt\n";
}

beman::optional::optional<int> opt{26};
for (const auto& i : opt) {
    // Should see this in console.
    std::cout << "\"for each loop\" over C++26 optional: opt = " << i << "\n";
}
```

Full code can be found in [./examples/range_loop.cpp](https://github.com/bemanproject/optional/blob/main/examples/range_loop.cpp). Build and run instructions in
[./examples/README.md](https://github.com/bemanproject/optional/blob/main/examples/README.md). Or try it on Compiler Explorer:  
  
https://godbolt.org/z/qdzz8Y7jT  
  
### optional_ref

The next code snippet shows optional reference support added in [`std::optional<T&>`
(P2988)](https://wg21.link/P2988):  

```cpp
#include <beman/optional/optional.hpp>
...

struct Cat { ... };

beman::optional::optional<Cat&> find_cat(std::string) { return {}; }
beman::optional::optional<Cat&> do_it(Cat& cat) { return { cat }; }

beman::optional::optional<Cat&> api() {
    beman::optional::optional<Cat&> cat = find_cat("Fido");
    return cat.and_then(do_it);
}

beman::optional::optional<Cat&> cat = api();

```

Full code can be found in [./examples/optional_ref.cpp](https://github.com/bemanproject/optional/blob/main/examples/optional_ref.cpp). Build and run instructions in [./examples/README.md](https://github.com/bemanproject/optional/blob/main/examples/README.md). Or try it on Compiler Explorer:  

https://godbolt.org/#z:OYLghAFBqd5QCxAYwPYBMCmBRdBLAF1QCcAaPECAMzwBtMA7AQwFtMQByARg9KtQYEAysib0QXACx8BBAKoBnTAAUAHpwAMvAFYTStJg1DIApACYAQuYukl9ZATwDKjdAGFUtAK4sGIAKwAbKSuADJ4DJgAcj4ARpjEAQCcpAAOqAqETgwe3r4BwemZjgLhkTEs8Yn%2BKXaYDtlCBEzEBLk%2BfkG2mPYlDE0tBGXRcQnJts2t7fldCpNDESOVYzUAlLaoXsTI7BwA9HsA1JiqrKn0CnuoqX1iAPrEmFQAdMipqYcAtABUn27W1h%2BnxMGgAggdDkJlAARAAan3COwYSk%2BAEksII8DQxodQakmMgEJhPmZnhpDgB1VEAFQAEodQqEAGoAWU%2BJx2N2yINBPPMAGYIshvFhDiZ%2BW54ixDFcuQIxLLbrRngh3uLsHywQKhSLMGKJXNiBFgOrNaDDV4HIc3EwCGKAOxWMGHF2HCJ20TNWioYB3CJYVQmR0aIPQ8VO3n2sP8iM85hsBT4naHOboLj2h2xsEQ5RGkiHIjWgGWMzBAtEw5oUUAd02tHQh29qAA1o28M29QQEHgFM8eRDFMbDsQmNXDul3QkFAXUMPMKlHkpBIdrkq51QEowdr3%2B0coqgCOxDoOjCnpa1x6hJ8Rp7WvPXDmIFLP4o/KwgrztSIdYl47YQ3QYAA3TwgMwadUGrSIb27D4lGlTFkB3LUwRtAhvkOGgGHQO5PQgVMQBAQ1jVWTM5wILYGEOBh71oG5iHDB0wxQ0E0Iw9BUD9AgIDQ8xAkrW1SKDCxyMosVS09RjQzNNjH1SPAICEx0eVda1bQwz19WhTD/Vw20IHMMwADE8A4wzVnDFTXSxQ4IE0sAwHFbSaNoOiCGIJSI1U1THgo4gqI4riIG%2BT0LJjKyXWk51XV8sSXLchjwq1KMzVDQ4IXjcCkz1VN0zNTLEwJHKCHQUtM13XEqEPYgi0sawyurQgEEOZQzCSAAOdqACV/G/Ls9SrPU7wfJtW1odtO27ZDwSOE9gEOfBHgcWgAE8VzlZhaBnOcF3Axg7VXbIxHXTcGG3PsWKlQxCMO%2BVaBujaxHFNxeNLdUdOwvTuIIoj3JIsjYv88qUpjJizSuvwQFuzaHqVZ7XsCd7AsIHjbT4gSCE80SgeEySQZEqLeTBCHYaO%2B6oce2h4bRt7%2BWwOSFM8iKf0wBDSbu9nNupgg%2BPezSnI%2BnC8MMkyzLMMwwq8mLMD8qjPWeQwcP6hgIGRzHLOS5iicjbSMtYLKipTEq3pY91DmlCJFPK6KXQhbBThYc49SoYhUBYFq2s6nqQHWtdHg3R4zswC7QVUkx/CsCPpRW%2BI7i8GilHQcOw38bTZO8jPM6z11PCF20tKNtN7UIph5MUjXQ9dcPI4saPY/jrxE%2BT5OWbZimlU5p6JQR97ImrL6C9TUsS7LyWzR8mWxJDJKdbNCEBR/Lw6AbE4znECqABJK2lDsvk%2BWtiGbKhvTHT5Pl2pQ7WAZBkE%2BKRdwqhfiHj44HadkBN8OZ5f2XvZr9vqQexV6OwuHsLqPQKRNWhJgWIqIGD8EVGTB4TwODrHuhwfwvA/AcC0KQVAnB/h1UsCmTY2w9QCh4KQAgmhUHrGbCASQ7VnhJH8Fwdq/h2GSCSJIQIXB/D8P0JwSQvAWABA0KQbBuD8EcF4AoEA4jqE4NQaQOAsAYCIBACceof4SDkEoC0YAChlCGB6EID8UFOCULQI7OgtpsjGMiLQMxkFJG8GsfJegiRDHMFSAoD8BBSDuLoAkKI%2BtOBuLdh4hIAB5P8ziLFKJCKoeooJiCGPCUk%2BoTR8DYN4PwQQIgxDsCkDIQQigVDqESboXqBgjAoGLDYcasQ5GwEyiACGdxoZiFIGBRI7l47NlWOsaGciOCfFTE5UwRCLCll4KgXpRosAtMUqQZ%2BmI2DUlQJ4ZZ6xnxbB2HoVMEQHGmPMdgyh1YRypEsco9BmCJE0LwZwe22iiA1VUO1QInxAiSEOP/Wy/SGCDNsoQqwlhvy4EIPmChqxeCKK0EM0gRImBYESCs%2Bh/hxHoOEaQURmKHmJOkbI%2BRVCaHrFURorRyAdFkAoBAAxRiTFOLOTcwJkTbF9BOcylxjygmeJQLU30gLmxspsZ40JbAMl8piXElliSqWpPSTIzJyBskRAyfk4QohxAlM1eUtQjzdDBEFfU6Z%2Bg8DNPgBANpHSum0B6WMYViKRmcHGSVSZDTZl4IWaZcC8B1hrMcBsrZtAdkbH2cUiYOSuXxPObwS5pcbloM4Pc1xTyOAvOpW8w4Hyvk/MrIKgFazgU8QaRC/A2aYVwrJesZFqLKDJo4DivF4i01EtsCS%2BFtDSD0K4BoLFnB%2BQiLEQSqRGSu2It7f2wRHAh2jrmeOmtDqbzZAYUAA

## How to Build

### Compiler Support

This is a modern C++ project which can be compiled with the latest C++ standards (**C++20 or later**).

Default build: `C++23`. Please check `etc/${compiler}-flags.cmake`.

### Dependencies

This project is mainly tested on `Ubuntu 22.04` and `Ubuntu 24.04`, but it should be as portable as CMake is. This project has no C or C++ dependencies.

Build-time dependencies:

* `cmake`
* `ninja`, `make`, or another CMake-supported build system
  * CMake defaults to "Unix Makefiles" on POSIX systems

Example of installation on `Ubuntu 24.04`:

```shell
# Install tools:
apt-get install -y cmake make ninja-build

# Example of toolchains:
apt-get install                           \
  g++-14 gcc-14 gcc-13 g++-13             \
  clang-18 clang++-18 clang-17 clang++-17
```

<details>
<summary> Build GoogleTest dependency from github.com </summary>

If you do not have GoogleTest installed on your development system, you may
optionally configure this project to download a known-compatible release of
GoogleTest from source and build it as well.

```shell
cmake -B build -S . -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=./cmake/use-fetch-content.cmake
```

The precise version of GoogleTest that will be used is maintained in
`./lockfile.json`.

</details>

### Instructions

Full set of supported toolchains can be found in [.github/workflows/ci.yml](https://github.com/bemanproject/optional/blob/main/.github/workflows/ci.yml).

#### Preset CMake Flows

This project strives to be as normal and simple a CMake project as possible. This build workflow in particular will work, producing a static `beman_optional` library, ready to package:

```shell
# List available preset configurations:
$ cmake --workflow --list-presets
Available workflow presets:

  "system"
  "gcc-14"
  "gcc-13"
  "clang-18"
  "clang-17"

# Run examples:
$ cmake --workflow --preset gcc-14
cmake --workflow --preset gcc-14
Executing workflow step 1 of 3: configure preset "gcc-14"
...
-- Build files have been written to: /path/to/repo/.build/gcc-14

Executing workflow step 2 of 3: build preset "gcc-14"

ninja: no work to do.

Executing workflow step 3 of 3: test preset "gcc-14"

Test project /path/to/repo/.build/gcc-14
        Start   1: OptionalTest.TestGTest
  1/... Test   #1: OptionalTest.TestGTest ...........................   Passed    0.00 sec
...
        Start   x: RangeSupportTest.RangeConcepts
.../... Test   #x: RangeSupportTest.RangeConcepts ...................   Passed    0.00 sec
        Start x+1: RangeSupportTest.IteratorConcepts
.../... Test #x+1: RangeSupportTest.IteratorConcepts ................   Passed    0.00 sec
...

100% tests passed, 0 tests failed out of ...

Total Test time (real) =   0.09 sec
```

This should build and run the tests with GCC 14 with the address and undefined behavior sanitizers enabled.

#### Custom CMake Flows

##### Build and Run Tests

CI current build and test flows:

```shell
# Configure build: default build production code + tests (OPTIONAL_ENABLE_TESTING=ON by default).
$ cmake -G "Ninja Multi-Config" \
      -DCMAKE_CONFIGURATION_TYPES="RelWithDebInfo;Asan" \
      -DCMAKE_TOOLCHAIN_FILE=etc/clang-19-toolchain.cmake \
      -B .build -S .
-- The CXX compiler identification is Clang 19.0.0
...
-- Build files have been written to: /path/to/optional/.build

# Build.
$ cmake --build .build --config Asan --target all -- -k 0
...
[30/30] Linking CXX executable ... # Note: 30 targets here (including tests).

# Run tests.
$ ctest --build-config Asan --output-on-failure --test-dir .build
Internal ctest changing into directory: /path/to/optional/.build
Test project /path/to/optional/.build
...
100% tests passed, 0 tests failed out of 82

Total Test time (real) =   0.67 sec
```

##### Build Production, but Skip Tests

By default, we build and run tests. You can provide `-DOPTIONAL_ENABLE_TESTING=OFF` and completely disable building tests:

```shell
# Configure build: build production code, skip tests (OPTIONAL_ENABLE_TESTING=OFF).
$ cmake -G "Ninja Multi-Config" \
      -DCMAKE_CONFIGURATION_TYPES="RelWithDebInfo;Asan" \
      -DCMAKE_TOOLCHAIN_FILE=etc/clang-19-toolchain.cmake \
      -DOPTIONAL_ENABLE_TESTING=OFF \
      -B .build -S .
-- The CXX compiler identification is Clang 19.0.0
...
-- Build files have been written to: /path/to/optional/.build

# Build.
$ cmake --build .build --config Asan --target all -- -k 0
...
[15/15] Linking CXX executable ... # Note: 15 targets here (tests were not built).

# Check that tests are not built/installed.
$ ctest --build-config Asan --output-on-failure --test-dir .build
Internal ctest changing into directory: /path/to/beman.optional/.build
Test project /path/to/beman.optional/.build
No tests were found!!!
```

#### Pre-Commit for Linting

Various linting tools are configured and installed via the [pre-commit](https://pre-commit.com/) framework. This requires a working python environment, but also allows the tools, such as clang-format and cmake-lint, to be versioned on a per project basis rather than being installed globally. Version changes in lint checks often means differences in success or failure between the versions in CI and the versions used by a developer. By using the same configurations, this problem is avoided.

In order to set up a python environment, using a python virtual environment can simplify maintaining different configurations between projects. There is no particular dependency on a particular python3 version.

##### Creating and configuring a venv

```shell
python3 -m venv .venv
. .venv/bin/activate && python3 -m pip install --upgrade pip setuptools wheel
. .venv/bin/activate && python3 -m pip install pip-tools
. .venv/bin/activate && python3 -m piptools sync requirements.txt
. .venv/bin/activate && python3 -m piptools sync requirements-dev.txt
. .venv/bin/activate && exec bash
```

This will create the venv, install the python and python development tools, and run bash with the PATH and other environment variables set to use the venv preferentially.

##### Running the linting tools

```shell
pre-commit run -a
```

This will download and configure the lint tools specified in .pre-commit-config.yaml.

There is also a Makefile that will automate this process and keep everything up to date.

```shell
make lint
```

## Papers

Latest revision(s) of the papers can be built / found at:

* [give-std-optional-range-support](https://github.com/neatudarius/give-std-optional-range-support/) for
`Give *std::optional* Range Support (P3168)`
  * issue: [#1831](https://github.com/cplusplus/papers/issues/1831)
  * LEWG:
    * Reviewed in Tokyo 2024.
    * Forwarded by LEWG April electronic poll to LWG.
  * LWG:
    * Reviewed and approved in Saint Louis 2024.
* [./papers/P2988/README.md](https://github.com/bemanproject/optional/blob/main/papers/P2988/README.md) for `std::optional<T&> (P2988)`.
  * issue: [#1661](https://github.com/cplusplus/papers/issues/1661)
  * LEWG:
    * Reviewed in Tokyo 2024.
    * Forwarded by LEWG in 2025 in Hagenberg.