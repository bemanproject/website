<!--
SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
-->

# Writing Documentation

Library documentation lives with the library. The website reads each configured repository, converts its Markdown with Pandoc, generates API reference pages with MrDocs, and assembles everything with Antora.

## Write the library overview

Every imported library gets an Overview page. Its repository `README.md` is included automatically. A useful README normally contains:

- what the library does;
- its maturity and supported C++ version;
- a small usage example;
- build and test instructions;
- links to proposals, design notes, and other documentation.

Use ordinary GitHub Markdown. Prefer headings, fenced code blocks, lists, tables, and normal Markdown links over raw HTML.

````markdown
## Example

```cpp
#include <beman/example/example.hpp>

auto result = beman::example::make_result();
```

See the [design notes](docs/design.md).
````

Repository-relative links are rewritten during import. Links to imported pages become documentation links; links to files that are not imported continue to point to GitHub.

## Add a library

1. Put the repository next to `website/` locally.
2. Add its repository name and prose pages to `beman_libraries_to_import.yaml`, keyed by your repository name.
3. Improve its `README.md` and public header comments.
4. Add `docs/mrdocs.yml` if the generated default is insufficient.
5. Build the complete site and inspect Overview, API Reference pages, and any other pages you may have added.

```shell
make install     # Python and npm dependencies
make start       # build and serve at http://127.0.0.1:8000
make build       # write the static site to build/
```

Pandoc and MrDocs must already be on `PATH` for local builds. Changes to Markdown or C++ comments require rebuilding the site.

## Add more prose pages

List additional Markdown files in `beman_libraries_to_import.yaml`:

```yaml
example:
  files:
    - docs/overview.md
    - docs/README.md: development.md
```

The key is your repository name, example names are `optional` and `execution`. A plain entry keeps its path below `docs/`. The `source: target` form renames the page in the generated site. Keep the library checkout next to the website checkout while developing:

```text
beman/
|-- website/
`-- example/
```

## Document the public API

MrDocs reads documentation comments from public C++ declarations. Use `/** ...
*/` for a block or `///` for a short comment. The first sentence is the summary;
put longer explanation after a blank line.

```cpp
/** Creates a result from a value.

    The returned result owns the supplied value.

    @tparam T The stored value type.
    @param[in] value The value to store.
    @returns A result containing `value`.
    @throws std::bad_alloc if storage cannot be allocated.
 */
template <class T>
result<T> make_result(T value);
```

The most useful commands are:

- `@param name` or `@param[in] name` for function parameters;
- `@tparam name` for template parameters;
- `@returns` for the return value;
- `@throws type` for exceptions;
- `@pre` and `@post` for contracts;
- `@code` and `@endcode` for a code example inside a comment.

Parameter names must match the declaration. Use backticks for identifiers and short code fragments. Document behavior and constraints rather than restating the signature.

See the MrDocs guides for [documenting code](https://mrdocs.com/docs/mrdocs/develop/commands/index.html), the [command reference](https://mrdocs.com/docs/mrdocs/develop/commands/reference.html), and [configuration options](https://mrdocs.com/docs/mrdocs/develop/configuration/reference.html).

## Configure MrDocs when needed

The website creates a basic MrDocs configuration for a library with an `include/` directory. Add `docs/mrdocs.yml` to the library repository when it needs custom include paths, symbol filters, generated headers, or compiler configuration. Keep public symbols included and implementation details excluded.
