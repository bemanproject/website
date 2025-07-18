---
sidebar_position: 2
---

<!--
SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
-->

# The Beman Standard

This document specifies rules and recommendations for Beman project libraries.
Its goal is to create consistency facilitating the evaluation of, and
contribution to Beman libraries.

## Introduction

### Core principles

This standard is driven by four core principles:

1. **[CORE.QUALITY] Highest quality**. Standards track libraries impact
   countless engineers and, consequently, should be of the highest quality.
2. **[CORE.PRODUCTION_READY] Production-ready**. Production feedback
   necessitates reliable, well-documented software.
3. **[CORE.INDUSTRY_STANDARD] Industry standard technology**. Where there's
   industry consensus on best practices, we should take advantage. Innovation in
   tooling and style is not our purpose.
4. **[CORE.INCLUSIVE] Welcoming and inclusive community**. Broad, useful
   feedback requires an unobstructed path for using, reviewing, and
   contributing to Beman libraries. This principle encompasses ergonomics,
   cross-industry participation, and cultural accommodation.

### Changing this document

This is a living document that adapts to evolving best practices and community
needs. To make changes:

1. Create a [discourse topic](https://discourse.boost.org) detailing the change
   and how it aligns with the core principles.
2. After some community discussion, create a PR with the actual change on
   [GitHub](https://github.com/bemanproject/beman) and apply the *Beman leads* label.
   The PR should also link to the discourse topic.
3. Continue discussions on the PR and discourse topic.
4. Await a leads decision based on the community feedback.

Note: When making minor changes such as fixing typos, correcting grammar mistakes or improving clarity, some of the previous steps may be skipped - a PR can be directly created.

### Conventions

This standard consists of entries that include an all-caps, dot-separated
identifier for referencing.

With the exception of the core principles, these entries are either rules or
recommendations.

- **Requirements** must be followed in order to conform to this standard. These entries
  are prefixed by "REQUIREMENT:".
- **Recommendations** should be followed in general, but specific circumstances
  may make this a less-than-ideal choice. Libraries not following a specific
  recommendation can still conform to this standard. These entries are prefixed
  by "RECOMMENDATION:".

## License

### **[LICENSE.APPROVED]**

**REQUIREMENT**: All Beman libraries must be licensed under an approved license. These are:

1. [Apache License v2.0 with LLVM Exceptions](https://llvm.org/LICENSE.txt)
2. [Boost Software License 1.0](https://www.boost.org/LICENSE_1_0.txt)
3. [The MIT License](https://opensource.org/license/mit)

Use the following format:

```markdown
==============================================================================
The Beman Project is under the Apache License v2.0 with LLVM Exceptions:
==============================================================================

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

... // actual license content

==============================================================================
Software from third parties included in the Beman Project:
==============================================================================
The Beman Project contains third party software which is under different license
terms. All such code will be identified clearly using at least one of two
mechanisms:
1) It will be in a separate directory tree with its own `LICENSE.txt` or
   `LICENSE` file at the top containing the specific license and restrictions
   which apply to that software, or
2) It will contain specific license and restriction terms at the top of every
   file.

```

Check [LICENSE.APACHE_LLVM](#licenseapache_llvm) for recommended license format.

### **[LICENSE.APACHE_LLVM]**

**RECOMMENDATION**: A Beman library should be licensed
under the `Apache License v2.0 with LLVM Exceptions`
(first recommended license in [LICENSE.APPROVED](#licenseapproved)).

Use the exact content from [beman/LICENSE](https://github.com/bemanproject/beman/blob/main/LICENSE)
into your library's `LICENSE` file.

### **[LICENSE.CRITERIA]**

**REQUIREMENT**: All approved licenses must meet the following requirements:

1. Simple to read and understand.
2. Permission without fee to copy, use and modify the software for any
   use (commercial and non-commercial).
3. Requires that the license appears on all copies of the software source code.
4. Must not require that the license appears with executables or other binary
   uses of the library.
5. Must not require that the source code be available for execution or other
   binary uses of the library.

## General

### **[LIBRARY.NAMES]**

**RECOMMENDATION**: Beman libraries names begin with `beman.` followed by a `snake_case` short name. It should not contain a target C++ version.

Examples: `beman.smart_pointer` and `beman.sender_receiver`.

Bad examples: `smart_pointer` or `beman.smartpointer` or `beman.optional26`.

## REPOSITORY

### **[REPOSITORY.NAME]**

**RECOMMENDATION**: The repository should be named after the library name excluding the `beman.` prefix. It should not contain a target C++ version.

Examples: A `beman.smart_pointer` library's repository should be named `smart_pointer`. A `beman.optional` library's repository should be named `optional`.

Bad examples: `smartpointer` or `optional26`.

### **[REPOSITORY.CODEOWNERS]**

**REQUIREMENT**: There must be a `.github/CODEOWNERS` file with a relevant set of codeowners. Please check [exemplar: CODEOWNERS](https://github.com/bemanproject/exemplar/blob/main/.github/CODEOWNERS).

### **[REPOSITORY.DEFAULT_BRANCH]**

**REQUIREMENT**: The repository must have `main` as default branch.

### **[REPOSITORY.DISALLOW_GIT_SUBMODULES]**

**RECOMMENDATION**: The repository should not use git submodules. Check `CMAKE.USE_FIND_PACKAGE` for alternatives.

Known exceptions:
* [mpark/wg21: Framework for Writing C++ Committee Papers](https://github.com/mpark/wg21): A non-C++ submodule designed for drafting ISO C++ papers using LaTeX or Markdown.

## Release

### **[RELEASE.GITHUB]**

**REQUIREMENT**: All Beman libraries must be released using [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github).

### **[RELEASE.NOTES]**

**RECOMMENDATION**: Release should include:

1. A title that clearly indicates the release version and purpose. (Check visual example for the field location.)

2. Description. (Check visual example for the field location.)

   2.1. An "About" section describing the main purpose and impact of the release.

   2.2. A "Release Maturity" section indicating the current status of the library according to the [Beman Library Maturity Model](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_LIBRARY_MATURITY_MODEL.md).

   2.3. A "Changelog" section listing all changes, organized by:
   - Breaking changes (if any)
   - New features and improvements
   - Bug fixes
   - Build system changes
   - Documentation updates

   2.4. A "New Contributors" section listing all first-time contributors.

   2.5. A "Full Changelog" link to the complete list of commits.

   2.6. A "Contributors" section listing all contributors to this release. Note: This section is autogenerated by GitHub Releases!

Use the following format:

```markdown
## About

<!-- TODO: Update this section and remove this comment. -->

## Release Maturity

<!-- TODO: Update this section and remove this comment. -->

This release has a status of [Under development and not yet ready for production use.](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_LIBRARY_MATURITY_MODEL.md#under-development-and-not-yet-ready-for-production-use).


## Changelog

<!-- TODO: Update this section and remove this comment. -->

* <description change> by @${USER} in https://github.com/bemanproject/${REPO}/pull/${PR_ID}
* ...

**Full Changelog**: https://github.com/bemanproject/${REPO}/compare/${PREV_VERSION}...${CURRENT_VERSION}

## New Contributors

<!-- TODO: Update this section and remove this comment. -->

* @${USER} made their first contribution in https://github.com/bemanproject/${REPO}/pull/#${PR_ID}
* ...

```

Complete examples can be found in [https://github.com/bemanproject/exemplar/releases](https://github.com/bemanproject/exemplar/releases).

Here is snapshot of notes for a particular release in `exemplar`:

![](/images/release-notes-examples.png)


### **[RELEASE.GODBOLT_TRUNK_VERSION]**

**RECOMMENDATION**: A Beman library should have at least a trunk version deployed on godbolt with nightyclone mode activated. Check [tutorial: Compiler Explorer Deployment](https://github.com/bemanproject/beman/blob/main/guidelines/compiler-explorer-deployment.md).


## Top-level

The top-level of a Beman library repository must consist of `CMakeLists.txt`, `LICENSE`, and `README.md` files.

### **[TOPLEVEL.CMAKE]**

**REQUIREMENT**: There must be a `CMakeLists.txt` file at the repository's root that builds and tests (via. CTest) the library.

### **[TOPLEVEL.LICENSE]**

**REQUIREMENT**: There must be a `LICENSE` file at the
repository's root with the contents of an approved license that covers the
contents of the repository.

### **[TOPLEVEL.README]**

**REQUIREMENT**: There must be a markdown-formatted
`README.md` file at the repository's root that describes the library, explains how
to build it, and links to further documentation.

## `README.md`

### **[README.TITLE]**

**RECOMMENDATION**: The `README.md` should begin with a level 1
header with the name of the library optionally followed with a ":" and short
description.

Examples:

```markdown
# beman.sender_receiver: Scalable Asychronous Program Building Blocks
```

### **[README.BADGES]**

**REQUIREMENT**: Following the title, the `README.md` must have a one-line badge list. Examples: library status (`[README.LIBRARY_STATUS]`), CI status, code coverage, Compiler Explorer example.

Example:
```markdown
![Library Status](https://raw.githubusercontent.com/bemanproject/beman/refs/heads/main/images/badges/beman_badge-beman_library_under_development.svg) ![Continuous Integration Tests](https://github.com/bemanproject/exemplar/actions/workflows/ci_tests.yml/badge.svg) ![Lint Check (pre-commit)](https://github.com/bemanproject/exemplar/actions/workflows/pre-commit.yml/badge.svg) [![Compiler Explorer Example](https://img.shields.io/badge/Try%20it%20on%20Compiler%20Explorer-grey?logo=compilerexplorer&logoColor=67c52a)](https://godbolt.org)
```

Use exactly one of the following entries for the library status badge:

```markdown
![Library Status](https://raw.githubusercontent.com/bemanproject/beman/refs/heads/main/images/badges/beman_badge-beman_library_under_development.svg)
```

or

```markdown
![Library Status](https://raw.githubusercontent.com/bemanproject/beman/refs/heads/main/images/badges/beman_badge-beman_library_production_ready_api_may_undergo_changes.svg)
```

or

```markdown
![Library Status](https://raw.githubusercontent.com/bemanproject/beman/refs/heads/main/images/badges/beman_badge-beman_library_production_ready_stable_api.svg)
```

or

```markdown
![Library Status](https://raw.githubusercontent.com/bemanproject/beman/refs/heads/main/images/badges/beman_badge-beman_library_retired.svg)
```

Use exactly one of the following entries for the standard target status badge:

```markdown
![Standard Target](https://github.com/bemanproject/beman/blob/main/images/badges/cpp26.svg)
```

or

```markdown
![Standard Target](https://github.com/bemanproject/beman/blob/main/images/badges/cpp29.svg)
```

If the library has been deployed onto Compiler Explorer, add this badge and replace the link with the link of the example code taken from Compiler Explorer:

```markdown
[![Compiler Explorer Example](https://img.shields.io/badge/Try%20it%20on%20Compiler%20Explorer-grey?logo=compilerexplorer&logoColor=67c52a)](https://godbolt.org)
```

### **[README.PURPOSE]**

**RECOMMENDATION**: Following the badges list and a newline, the `README.md` should contain a one line summary describing the library's purpose.

### **[README.IMPLEMENTS]**

**RECOMMENDATION**: Following the purpose and a newline, the
`README.md` should indicate which papers the repository implements. Use the following style:

```markdown
**Implements**: [`std::optional<T&>` (P2988R5)](https://wg21.link/P2988R5) and
[Give *std::optional* Range Support (P3168R1)](https://wg21.link/P3168R1).
```

### **[README.LIBRARY_STATUS]**

**REQUIREMENT**: Following the implements section and a newline, the `README.md` must indicate the **current** library status with respect to the [Beman library maturity model](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_LIBRARY_MATURITY_MODEL.md). An extra badge must be added to the `README.md` to visually indicate the library status (check `[README.BADGES]`). Note: The full library status history can be found in the GitHub release notes.

Use exactly one of the following entries for the status line:

```markdown
**Status**: [Under development and not yet ready for production use.](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_LIBRARY_MATURITY_MODEL.md#under-development-and-not-yet-ready-for-production-use)
```

or

```markdown
**Status**: [Production ready. API may undergo changes.](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_LIBRARY_MATURITY_MODEL.md#production-ready-api-may-undergo-changes)
```

or

```markdown
**Status**: [Production ready. Stable API.](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_LIBRARY_MATURITY_MODEL.md#production-ready-stable-api)
```

or

```markdown
**Status**: [Retired. No longer maintained or actively developed.](https://github.com/bemanproject/beman/blob/main/docs/BEMAN_LIBRARY_MATURITY_MODEL.md#retired-no-longer-maintained-or-actively-developed)
```

## CMake

### **[CMAKE.DEFAULT]**

**RECOMMENDATION**: The root `CMakeLists.txt` should build all targets by default (including dependency targets).

### **[CMAKE.USE_FIND_PACKAGE]**

**RECOMMENDATION**: The root `CMakeLists.txt` should fetch all dependency targets via [CMake `find_package`](https://cmake.org/cmake/help/latest/command/find_package.html).

Use the following style:

```CMake
find_package(<PackageName> [REQUIRED])
```

See `[CMAKE.SKIP_TESTS]` in this document for a working example or [exemplar/blob/main/CMakeLists.txt](https://github.com/bemanproject/exemplar/blob/main/CMakeLists.txt).


### **[CMAKE.PROJECT_NAME]**

**RECOMMENDATION**: The CMake project name should be identical to the beman library name.

### **[CMAKE.PASSIVE_PROJECTS]**

**REQUIREMENT**: CMake projects must not adjust user-specified compilation flags.

User-provided compilation flags, whether specified via presets, command-line
options, or toolchains, must not be modified by CMake projects. Therefore, CMake
projects may not set variables that impact compilation flags such as
`CMAKE_CXX_FLAGS` and `CMAKE_CXX_STANDARD`, as this would override user settings.

For common compiler/flag combinations, it is recommended to provide CMake presets
as a convenient alternative for users.

If specific compiler flags are essential for project functionality (e.g., C++
standard features), use utilities like `check_cxx_source_compiles` to detect
support and provide a helpful error message suggesting appropriate flags for the
user's compiler.

### **[CMAKE.LIBRARY_NAME]**

**RECOMMENDATION**: The CMake library target's name should
be identical to the library name.

Examples:

```CMake
add_library(beman.smart_pointer STATIC)
#...
```

### **[CMAKE.LIBRARY_ALIAS]**

**REQUIREMENT**: The CMake code must create an alias of
the library target named `beman::<short_name>`. This target is intended for
external use.

Examples:

```CMake
add_library(beman::smart_pointer ALIAS beman.smart_pointer)
#...
```

### **[CMAKE.TARGET_NAMES]**

**RECOMMENDATION**: All targets, aside from the library target, should begin with a `<library_name>.` prefix

```CMake
add_executable(beman.smart_pointer.examples.basic)
#...
add_executable(beman.smart_pointer.tests.roundtrip)
#...
```

### **[CMAKE.PASSIVE_TARGETS]**

**REQUIREMENT**: External targets must not modify compilation flags of dependents.

Therefore, `target_compile_features` (e.g., `cxx_std_20`) must not be used
because it modifies the compilation environment of dependent targets. Compiler
support for required features should be determined at CMake configuration time
using `check_cxx_source_compiles`.

Furthermore, `target_compile_definitions` with `PUBLIC` or `INTERFACE`
visibility must not be used, as these definitions are also propagated to
dependent targets. Preprocessor definitions intended for external use should be
generated into a `config.hpp` file at CMake configuration time. This
`config.hpp` should then be included by public headers.

### **[CMAKE.CONFIG]**

**REQUIREMENT**: At `install` time, a
`<library_name>-config.cmake` must be created which exports a
`beman::<short_name>` target.

### **[CMAKE.SKIP_TESTS]**

**RECOMMENDATION**: The root `CMakeLists.txt` should not build tests and their dependencies when `BEMAN_<short_name>_BUILD_TESTS` is set to `OFF` (see [CTest docs](https://cmake.org/cmake/help/latest/module/CTest.html) - similar to cmake's `BUILD_TESTING`). The option is prefixed with the project so that projects can compose. Turning on testing for the top level project should not turn on testing for dependencies. Since testing is part of the normal development workflow it is appropriate to set the option on by default for the top level project.

Use the following style:

```CMake
# File: <repo>/CMakeLists.txt
# ...
option(
    BEMAN_<short_name>_BUILD_TESTS
    "Enable building tests and test infrastructure. Default: ${PROJECT_IS_TOP_LEVEL}. Values: { ON, OFF }."
    ${PROJECT_IS_TOP_LEVEL}
)
# ...
if(BEMAN_<short_name>_BUILD_TESTS)
  add_subdirectory(tests)
endif()
```

The `CMakeLists.txt` in the test directory can declare any test-only dependendencies
that are required. For instance:


```CMake
# File: <repo>/tests/CMakeLists.txt
# ...
find_package(GoogleTest REQUIRED)

add_executable(myrepo-tests)
# ...
gtest_discover_tests(myrepo-tests)
```

### **[CMAKE.SKIP_EXAMPLES]**

**RECOMMENDATION**: The root `CMakeLists.txt` should not build examples and their dependencies when `BEMAN_<short_name>_BUILD_EXAMPLES` is set to `OFF`. The option is prefixed with the project so that projects can compose. Turning on examples for the top level project should not turn on examples for dependencies.

Use the following style:

```CMake
# <repo>/CMakeLists.txt
# ...
option(
    BEMAN_<short_name>_BUILD_EXAMPLES
    "Enable building examples. Default: ${PROJECT_IS_TOP_LEVEL}. Values: { ON, OFF }."
    ${PROJECT_IS_TOP_LEVEL}
)

# add actual code to be build here
...

# ...
if(BEMAN_<short_name>_BUILD_EXAMPLES)
  add_subdirectory(examples)
endif()
```

### **[CMAKE.AVOID_PASSTHROUGHS]**

**RECOMMENDATION**: Avoid `CMakeLists.txt` files consisting of a single `add_subdirectory` call.

In other words prefer,

```CMake
# <repo>/CMakeLists.txt
# ...
add_subdirectory(src/beman/optional)
```

to,

```CMake
# <repo>/CMakeLists.txt
# ...
add_subdirectory(src) # Don't do this

# <repo>/src/CMakeLists.txt
add_subdirectory(beman) # Don't do this

# <repo>/src/beman/CMakeLists.txt
add_subdirectory(optional) # Don't do this
```

## Directory layout

### **[DIRECTORY.INTERFACE_HEADERS]**

**REQUIREMENT**: Header files that are part of the public interface must reside within the `include/beman/<short_name>/` directory.

Examples:

```shell
include
└── beman
    └── exemplar
        └── identity.hpp
        └── ...
        └── ...
```

### **[DIRECTORY.IMPLEMENTATION_HEADERS]**

**REQUIREMENT**: Header files residing within `include/beman/<short_name>/` that are not part of the public interface
must either begin with `detail_` or reside within a subdirectory of
`include/beman/<short_name>/` called `detail` or begins with `detail_`.

Examples:

```shell
include
└── beman
    └── optional
        ├── detail                           # Private implementation subdirectory.
        │   ├── iterator.hpp
        │   └── stl_interfaces
        │       ├── config.hpp
        │       ├── fwd.hpp
        │       └── iterator_interface.hpp
        └── optional.hpp                     # Public interface.
```

### **[DIRECTORY.SOURCES]**

**REQUIREMENT**: If present, sources and headers not part of the
public interface should reside in the top-level `src/` directory, and should use
the same structure from `include/` - e.g., `src/beman/<short_name>/`. Check `CMAKE.AVOID_PASSTHROUGHS`.

Examples:

```shell
src
└── beman
    └── exemplar
        ├── CMakeLists.txt
        └── identity.cpp

src
└── beman
    └── optional
        ├── CMakeLists.txt
        ├── detail
        │   └── iterator.cpp
        └── optional.cpp
```

### **[DIRECTORY.TESTS]**

**REQUIREMENT**: All test files must reside within the top-level `tests/`
directory, and should use the same structure from `include/`. If multiple test types are present,
subdirectories can be made (e.g., unit tests, performance etc). Each project must have at least
one relevant test.

Examples:

```shell
tests
└── beman
    └── exemplar
        └── identity.test.cpp

tests
└── beman
    └── optional
        ├── CMakeLists.txt
        ├── detail
        │   └── iterator.test.cpp
        ├── optional.test.cpp
        ├── optional_constexpr.test.cpp
        ├── optional_monadic.test.cpp
        ├── optional_range_support.test.cpp
        ├── test_types.cpp
        ├── test_types.hpp
        ├── test_utilities.cpp
        └── test_utilities.hpp
```

### **[DIRECTORY.EXAMPLES]**

**REQUIREMENT**: All example files must reside within the top-level `examples/`
directory. Each project must have at least one relevant example.

Examples:

```shell
examples
├── CMakeLists.txt
├── identity_as_default_projection.cpp
└── identity_direct_usage.cpp
```

### **[DIRECTORY.DOCS]**

**REQUIREMENT**: If present, all documentation files, except the root `README.md`, must reside within the top-level `docs/` directory. If multiple docs types are present, subdirectories can be made (e.g., dev, public/private etc).

Examples:

```shell
docs
├── debug
│   └── ci.md
├── dev
│   └── lint.md
├── local.md
└── optional.md
```

### **[DIRECTORY.PAPERS]**

**REQUIREMENT**: If present, all paper related files (e.g., WIP LaTeX/Markdown projects for ISO Standardization), must reside within the top-level `papers/` directory.

Examples:

```shell
papers
└── P2988
    ├── Makefile
    ├── README.md
    ├── abstract.bst
    ...
```

## File layout

### **[FILE.NAMES]**

**RECOMMENDATION**: Source code and header should use the `snake_case` naming convention (similar to `LIBRARY.NAMES`).

Examples: `identity.hpp`, `identity.cpp`, `iterator_interface.hpp` or `optional_range_support.test.cpp`.

### **[FILE.TEST_NAMES]**

**REQUIREMENT**: Test source code files must use the `*.test.cpp` naming convention.

Examples: `identity.test.cpp`, `optional_ref.test.cpp` or `optional_range_support.test.cpp`.

### **[FILE.LICENSE_ID]**

**REQUIREMENT**: The [SPDX license identifier](https://spdx.dev/learn/handling-license-info/) must be added at the
first possible line in all files which can contain a comment
(e.g., C++, scripts, CMake/Makefile, YAML/YML, JASON, XML, HTML, LaTeX, Dockerfile etc).

Examples:

* C++ files shall use the following form:

```C++
// SPDX-License-Identifier: <SPDX License Expression>
```

* CMake files and scripts shall use the following form:

```CMake
# SPDX-License-Identifier: <SPDX License Expression>
```

* Markdown files will use a comment following the title:

```markdown
# Title

<!--
SPDX-License-Identifier: <SPDX License Expression>
-->
```

### **[FILE.COPYRIGHT]**

**RECOMMENDATION**: Source code files should NOT include a copyright notice following the SPDX license identifier.

## C++

### **[CPP.NAMESPACE]**

**RECOMMENDATION**: Headers in `include/beman/<short_name>/` should export
entities in the `beman::<short_name>` namespace.

### **[CPP.NO_FLAG_FORKING]**

**REQUIREMENT**: C++ preprocessing must produce identical output regardless of compiler flags.

Therefore, feature test macros such as `__cpp_explicit_this_parameter` should
not be used directly. Instead use the following approach for feature-dependent
code generation:

1. Check for availability at CMake time using, for example,
   `check_cxx_source_compiles`.
2. Create a CMake `option` (e.g. `BEMAN_<short_name>_USE_DEDUCING_THIS`)
   with a default value based on detected support.
3. Generate a `config.hpp` with a `#define` macro set to the selected option.
4. Use this macro in place of the feature test macro.

See
[beman.iterator_interface](https://github.com/bemanproject/iterator_interface/blob/5e6714e10faa1799723669e04abec6e75adbdb89/CMakeLists.txt#L44)
for an example.

### **[CPP.EXTENSION_IDENTIFIERS]**

**RECOMMENDATION**: For functionality that is not being recommended for standardization, but is an extension provided by the library, its identifiers should be prefixed with `ext_`.
