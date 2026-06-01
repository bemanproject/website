#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from __future__ import annotations

import argparse
import html
import posixpath
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="MrDocs AsciiDoc output directory")
    parser.add_argument(
        "--component-title",
        default="",
        help="Antora component title to use in generated API index titles",
    )
    return parser.parse_args()


def safe_component(name: str) -> str:
    stem = Path(name).stem
    suffix = "".join(Path(name).suffixes)
    if not stem.startswith("_"):
        return name
    leading = len(stem) - len(stem.lstrip("_"))
    safe_stem = "_".join(["underscore"] * leading + [stem.lstrip("_") or "symbol"])
    return safe_stem + suffix


def safe_target_path(target: str) -> str:
    return "/".join(safe_component(part) for part in target.split("/"))


def normalize_underscore_paths(root: Path) -> None:
    for path in sorted(
        root.rglob("*"),
        key=lambda item: len(item.relative_to(root).parts),
        reverse=True,
    ):
        safe_name = safe_component(path.name)
        if safe_name != path.name:
            path.rename(path.with_name(safe_name))


def rewrite_xref(match: re.Match[str]) -> str:
    target = match.group(1)
    anchor = match.group(2) or ""
    if ":" in target:
        return match.group(0)
    normalized = posixpath.normpath(target).lstrip("./")
    while normalized.startswith("../"):
        normalized = normalized[3:]
    if normalized.startswith("reference/"):
        normalized = normalized.removeprefix("reference/")
    normalized = safe_target_path(normalized)
    return f"xref:reference/{normalized}{anchor}["


def clean_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    title = re.sub(r"[`*_#]+", "", title)
    return html.unescape(title).strip()


def title_from_path(root: Path, path: Path, component_title: str) -> str:
    relative = path.relative_to(root).with_suffix("")
    if relative.name == "index":
        return (
            f"API Reference :: {component_title}"
            if component_title
            else "API Reference"
        )
    parts = list(relative.parts)
    if len(parts) <= 2:
        return "::".join(parts) + " namespace"
    name = re.sub(r"-[0-9a-f]+$", "", parts[-1])
    return "::".join(parts[:-1] + [name])


def first_plain_title(lines: list[str]) -> tuple[int | None, str | None]:
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("=", "[", "|", ".", ":", "include::", "xref:")):
            return None, None
        if stripped in {"----", "|==="}:
            return None, None
        if len(stripped) > 180:
            return None, None
        return index, clean_title(stripped)
    return None, None


def ensure_document_title(
    root: Path, path: Path, content: str, component_title: str
) -> str:
    if content.lstrip().startswith("= "):
        return content
    lines = content.splitlines()
    title_index, title = first_plain_title(lines)
    if title:
        del lines[title_index]
        if title_index < len(lines) and not lines[title_index].strip():
            del lines[title_index]
    else:
        title = title_from_path(root, path, component_title)
    body = "\n".join(lines).lstrip("\n")
    return f"= {title}\n\n{body}\n"


def single_namespace_child(root: Path, path: Path) -> Path | None:
    content = path.read_text()
    section_matches = list(re.finditer(r"^== ([^\n]+)$", content, flags=re.MULTILINE))
    direct_sections = [
        match.group(1)
        for match in section_matches
        if not re.fullmatch(r"xref:[^\[]+\[[^\]]+\] namespace", match.group(1))
    ]
    if direct_sections != ["Namespaces"]:
        return None

    namespace_section = next(
        match for match in section_matches if match.group(1) == "Namespaces"
    )
    next_section = next(
        (
            match
            for match in section_matches
            if match.start() > namespace_section.start()
        ),
        None,
    )
    section_content = content[
        namespace_section.end() : next_section.start() if next_section else len(content)
    ]
    targets = re.findall(
        r"^\|\s*xref:([^\[]+\.adoc)(?:#[^\[]*)?\[",
        section_content,
        flags=re.MULTILINE,
    )
    if len(targets) != 1:
        return None

    target = targets[0]
    if target.startswith("reference/"):
        target = target.removeprefix("reference/")
    child = (root / target).resolve()
    try:
        child.relative_to(root)
    except ValueError:
        return None
    return child if child.is_file() else None


def add_page_aliases(path: Path, aliases: list[str]) -> None:
    lines = path.read_text().splitlines()
    if not lines or not lines[0].startswith("= "):
        return
    lines.insert(1, f":page-aliases: {', '.join(aliases)}")
    path.write_text("\n".join(lines) + "\n")


def collapse_single_namespace_entrypoint(root: Path) -> None:
    entrypoint = root / "index.adoc"
    if not entrypoint.is_file():
        return

    wrappers: list[Path] = []
    current = entrypoint
    visited: set[Path] = set()
    while current not in visited:
        visited.add(current)
        child = single_namespace_child(root, current)
        if child is None:
            break
        wrappers.append(current)
        current = child

    if not wrappers:
        return

    aliases = [f"reference/{path.relative_to(root).as_posix()}" for path in wrappers]
    add_page_aliases(current, aliases)
    for wrapper in wrappers:
        wrapper.unlink()


def fix_adoc_file(root: Path, path: Path, component_title: str) -> None:
    content = path.read_text()
    content = re.sub(
        r"xref:([A-Za-z0-9_./-]+\.adoc)(#[^\[]*)?\[", rewrite_xref, content
    )
    content = ensure_document_title(root, path, content, component_title)
    path.write_text(content)


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    normalize_underscore_paths(root)
    for path in root.rglob("*.adoc"):
        fix_adoc_file(root, path, args.component_title)
    collapse_single_namespace_entrypoint(root)


if __name__ == "__main__":
    main()
