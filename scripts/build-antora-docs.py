#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from __future__ import annotations

import argparse
import html
import posixpath
import re
import shlex
import shutil
import subprocess  # nosec B404
from dataclasses import dataclass
from pathlib import Path

import yaml

WEBSITE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPOS_ROOT = WEBSITE_ROOT.parent
DEFAULT_WORK_ROOT = WEBSITE_ROOT / "build" / "antora-docs-work"
DEFAULT_OUTPUT_DIR = WEBSITE_ROOT / "build" / "docs"
DEFAULT_CACHE_DIR = WEBSITE_ROOT / "build" / "antora-cache"
MANIFEST_PATH = WEBSITE_ROOT / "beman_libraries_to_import.yaml"

PROJECT_DOCS = [
    ("README.md", "index.adoc", "Beman Docs"),
    (
        "beman_library_maturity_model.md",
        "beman_library_maturity_model.adoc",
        "Beman Library Maturity Model",
    ),
    ("beman_standard.md", "beman_standard.adoc", "Beman Standard"),
    ("mission.md", "mission.adoc", "Mission"),
    ("faq.md", "faq.adoc", "FAQ"),
    ("governance.md", "governance.adoc", "Governance"),
    ("code_of_conduct.md", "code_of_conduct.adoc", "Code of Conduct"),
]

SPECIAL_LABELS = {
    "debug-ci": "Debugging CI",
    "using_exemplar": "Using Exemplar",
    "using_cstring_view": "Guide",
    "design_rationale": "Design Rationale",
}

MRDOCS_CONFIG_PATH = "docs/mrdocs.yml"
MRDOCS_EXTRA_INCLUDES = {
    "task": ["../../execution/include"],
}


def render_mrdocs_config(repo_name: str, staged_repo: Path) -> str:
    includes = ["../include", *MRDOCS_EXTRA_INCLUDES.get(repo_name, [])]
    include_lines = "\n".join(f"  - {include}" for include in includes)
    return f"""# $schema: https://mrdocs.com/docs/mrdocs/develop/_attachments/mrdocs.schema.json
# yaml-language-server: $schema=https://mrdocs.com/docs/mrdocs/develop/_attachments/mrdocs.schema.json

---
source-root: ..
input:
  - ../include
exclude:
  - ../include/beman/{repo_name}/detail
  - ../tests/**
  - ../examples/**
exclude-patterns:
  - ../include/**/detail/**
  - ../tests/**
  - ../examples/**
includes:
{include_lines}
file-patterns:
  - '*.hpp'
  - '*.h'
include-symbols:
  - 'beman::**'
implementation-defined:
  - 'beman::detail'
  - 'beman::*::detail'
  - 'beman::*::detail::**'
multipage: true
generator: adoc
output: adoc
embedded: true
"""


MARKDOWN_LINK_RE = re.compile(
    r"(?P<prefix>!?\[[^\]]*\]\()(?P<href>[^\s)]+)(?P<suffix>(?:\s+[^)]*)?\))"
)
GITHUB_BLOB_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<branch>[^/]+)/(?P<path>.+)$"
)
DETAIL_TAG_RE = re.compile(r"<\s*(/?)\s*(details|summary)\b[^>]*>", re.IGNORECASE)
FENCE_START_RE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class HtmlTag:
    name: str
    start: int
    end: int
    closing: bool


@dataclass(frozen=True)
class DetailsBlock:
    summary: str
    body: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repos-root", type=Path, default=DEFAULT_REPOS_ROOT)
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--site-url", default="http://localhost:8000/docs")
    parser.add_argument("--clone-missing", action="store_true")
    parser.add_argument("--update-repos", action="store_true")
    parser.add_argument("--skip-api-reference", action="store_true")
    return parser.parse_args()


def run_command(*args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(*args, **kwargs)  # nosec B603 B607


def require_tool(name: str, install_hint: str) -> None:
    if shutil.which(name):
        return
    raise SystemExit(f"Missing required tool: {name}\n{install_hint}")


def check_tools(skip_api_reference: bool) -> None:
    require_tool("git", "Install git and ensure it is on PATH.")
    require_tool("pandoc", "Install Pandoc and ensure it is on PATH.")
    require_tool("npx", "Install Node.js/npm and run npm install in website/.")
    if not skip_api_reference:
        require_tool("mrdocs", "Install MrDocs and ensure it is on PATH.")


def load_manifest() -> dict:
    return yaml.safe_load(MANIFEST_PATH.read_text()) or {}


def parse_file_entry(entry) -> tuple[Path, Path]:
    if isinstance(entry, str):
        source_rel = Path(entry)
        target_rel = (
            Path(*source_rel.parts[1:])
            if source_rel.parts and source_rel.parts[0] == "docs"
            else source_rel
        )
        return source_rel, target_rel.with_suffix(".adoc")
    if isinstance(entry, dict) and len(entry) == 1:
        [(source, target)] = entry.items()
        return Path(source), Path(target).with_suffix(".adoc")
    raise ValueError(f"Unsupported file entry: {entry!r}")


def make_sidebar_label(target_name: str) -> str:
    stem = Path(target_name).stem
    if stem.lower() == "readme":
        return "README"
    if stem.lower() == "overview":
        return "Guide"
    if stem in SPECIAL_LABELS:
        return SPECIAL_LABELS[stem]
    return stem.replace("_", " ").replace("-", " ").title()


def component_name(repo_name: str) -> str:
    return f"beman.{repo_name}"


def ensure_source_repo(
    repo_path: Path, repo_name: str, clone_missing: bool, update_repos: bool
) -> None:
    repo_url = f"https://github.com/bemanproject/{repo_name}"
    if not repo_path.exists() and clone_missing:
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        run_command(
            [
                "git",
                "clone",
                "--branch",
                "main",
                "--single-branch",
                repo_url,
                str(repo_path),
            ],
            check=True,
        )

    if not repo_path.exists():
        raise SystemExit(f"Missing library checkout: {repo_path}")

    if update_repos:
        run_command(["git", "fetch", "origin", "main"], cwd=repo_path, check=True)
        run_command(["git", "checkout", "main"], cwd=repo_path, check=True)
        run_command(
            ["git", "pull", "--ff-only", "origin", "main"], cwd=repo_path, check=True
        )


def copy_repo(source: Path, target: Path) -> None:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(
            ".git",
            "build",
            "docs/html",
            "docs/latex",
            "docs/build",
            "__pycache__",
        ),
    )


def prepare_staged_mrdocs_inputs(staged_repo: Path, repo_name: str) -> Path:
    if repo_name == "transform_view":
        write_text(
            staged_repo
            / "include"
            / "beman"
            / "transform_view"
            / "config_generated.hpp",
            "\n".join(
                [
                    "// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception",
                    "",
                    "#ifndef BEMAN_TRANSFORM_VIEW_CONFIG_GENERATED_HPP",
                    "#define BEMAN_TRANSFORM_VIEW_CONFIG_GENERATED_HPP",
                    "",
                    "#define BEMAN_TRANSFORM_VIEW_USE_MODULES() 0",
                    "",
                    "#endif",
                    "",
                ]
            ),
        )

    mrdocs_config = staged_repo / MRDOCS_CONFIG_PATH
    if not mrdocs_config.exists():
        write_text(mrdocs_config, render_mrdocs_config(repo_name, staged_repo))
    ensure_mrdocs_embedded_output(mrdocs_config)
    return mrdocs_config


def ensure_mrdocs_embedded_output(mrdocs_config: Path) -> None:
    content = mrdocs_config.read_text()
    embedded_re = re.compile(r"(?m)^embedded:\s*(?:true|false)\s*$")
    if embedded_re.search(content):
        content = embedded_re.sub("embedded: true", content)
    else:
        content = content.rstrip() + "\nembedded: true\n"
    write_text(mrdocs_config, content)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def strip_frontmatter(content: str) -> str:
    if not content.startswith("---\n"):
        return content
    end = content.find("\n---\n", 4)
    if end == -1:
        return content
    return content[end + len("\n---\n") :].lstrip("\n")


def split_link_target(href: str) -> tuple[str, str]:
    for separator in ("#", "?"):
        if separator in href:
            path, rest = href.split(separator, 1)
            return path, separator + rest
    return href, ""


def is_external_or_anchor(href: str) -> bool:
    return (
        not href
        or href.startswith("#")
        or href.startswith("//")
        or bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href))
    )


def normalize_repo_relative_path(path: str) -> str:
    return path.removeprefix("./")


def rewrite_markdown_links_outside_fences(content: str, replacer) -> str:
    rewritten_blocks = []
    in_fence = False
    for line in content.splitlines(keepends=True):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            rewritten_blocks.append(line)
            continue
        rewritten_blocks.append(
            line if in_fence else MARKDOWN_LINK_RE.sub(replacer, line)
        )
    return "".join(rewritten_blocks)


def rewrite_github_blob_image_links(content: str) -> str:
    def replace(match: re.Match) -> str:
        if not match.group("prefix").startswith("!"):
            return match.group(0)

        href = match.group("href")
        pathless_href, suffix = split_link_target(href)
        github_match = GITHUB_BLOB_URL_RE.match(pathless_href)
        if not github_match:
            return match.group(0)

        href = (
            "https://raw.githubusercontent.com/"
            f"{github_match.group('owner')}/"
            f"{github_match.group('repo')}/"
            f"{github_match.group('branch')}/"
            f"{github_match.group('path')}"
            f"{suffix}"
        )
        return f"{match.group('prefix')}{href}{match.group('suffix')}"

    return rewrite_markdown_links_outside_fences(content, replace)


def github_relative_url(
    repo_url: str, repo_branch: str, path: str, is_image: bool
) -> str:
    if is_image:
        return f"{repo_url}/raw/{repo_branch}/{path}"
    kind = "tree" if path.endswith("/") or "." not in Path(path).name else "blob"
    return f"{repo_url}/{kind}/{repo_branch}/{path}"


def rewrite_library_markdown_links(
    content: str,
    repo_url: str,
    repo_branch: str,
    source_link_map: dict[str, str],
    source_rel: Path,
) -> str:
    source_dir = source_rel.parent.as_posix()

    def candidate_repo_paths(path: str) -> list[str]:
        normalized = normalize_repo_relative_path(path)
        candidates = [normalized]
        if source_dir and source_dir != ".":
            candidates.append(posixpath.normpath(posixpath.join(source_dir, path)))
        return list(dict.fromkeys(candidates))

    def replace(match: re.Match) -> str:
        href = match.group("href")
        if href.startswith("`") and href.endswith("`"):
            href = href[1:-1]
        if is_external_or_anchor(href):
            return match.group(0)

        path, suffix = split_link_target(href)
        candidates = candidate_repo_paths(path)
        synced_path = next(
            (candidate for candidate in candidates if candidate in source_link_map), ""
        )
        if synced_path:
            href = source_link_map[synced_path] + suffix
        else:
            href = github_relative_url(
                repo_url,
                repo_branch,
                candidates[-1],
                is_image=match.group("prefix").startswith("!"),
            )
            if suffix:
                href += suffix

        return f"{match.group('prefix')}{href}{match.group('suffix')}"

    return rewrite_markdown_links_outside_fences(content, replace)


def rewrite_project_markdown_links(
    content: str, source_rel: Path, source_link_map: dict[str, str]
) -> str:
    replacements = {
        "](/images/": "](images/",
        "](../images/": "](images/",
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    content = rewrite_github_blob_image_links(content)
    source_dir = source_rel.parent.as_posix()

    def candidate_project_paths(path: str) -> list[str]:
        normalized = normalize_repo_relative_path(path).removeprefix("docs/")
        candidates = [normalized]
        if source_dir and source_dir != ".":
            candidates.append(
                posixpath.normpath(posixpath.join(source_dir, normalized))
            )
        return list(dict.fromkeys(candidates))

    def replace(match: re.Match) -> str:
        href = match.group("href")
        if is_external_or_anchor(href) or match.group("prefix").startswith("!"):
            return match.group(0)

        path, suffix = split_link_target(href)
        synced_path = next(
            (
                candidate
                for candidate in candidate_project_paths(path)
                if candidate in source_link_map
            ),
            "",
        )
        if not synced_path:
            return match.group(0)

        href = source_link_map[synced_path] + suffix
        return f"{match.group('prefix')}{href}{match.group('suffix')}"

    return rewrite_markdown_links_outside_fences(content, replace)


def normalize_adoc_heading_sequence(content: str) -> str:
    lines = []
    previous_level = 1
    delimiter_stack = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped in {"----", "...."} or re.fullmatch(r"={4,}", stripped):
            if delimiter_stack and delimiter_stack[-1] == stripped:
                delimiter_stack.pop()
            else:
                delimiter_stack.append(stripped)
            lines.append(line)
            continue

        match = re.match(r"^(={2,6})\s+(.+)$", line)
        if match and not delimiter_stack:
            level = len(match.group(1))
            if level > previous_level + 1:
                level = previous_level + 1
                line = f"{'=' * level} {match.group(2)}"
            previous_level = level
        lines.append(line)
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")


def postprocess_pandoc_adoc(content: str) -> str:
    content = content.replace("link:xref:", "xref:")
    content = re.sub(
        r"link:([A-Za-z0-9_./-]+\.adoc)(#[^\[]*)?\[", r"xref:\1\2[", content
    )
    content = content.replace("\\_", "_")
    return content


def markdown_html_tags(content: str) -> list[HtmlTag]:
    tags = []
    offset = 0
    in_fence = False
    for line in content.splitlines(keepends=True):
        if FENCE_START_RE.match(line):
            in_fence = not in_fence
            offset += len(line)
            continue
        if not in_fence:
            for match in DETAIL_TAG_RE.finditer(line):
                tags.append(
                    HtmlTag(
                        name=match.group(2).lower(),
                        start=offset + match.start(),
                        end=offset + match.end(),
                        closing=bool(match.group(1)),
                    )
                )
        offset += len(line)
    return tags


def split_markdown_details(content: str) -> list[str | DetailsBlock]:
    tags = markdown_html_tags(content)
    if not any(tag.name == "details" and not tag.closing for tag in tags):
        return [content]

    def matching_details_close(open_index: int) -> int | None:
        depth = 1
        for index in range(open_index + 1, len(tags)):
            tag = tags[index]
            if tag.name != "details":
                continue
            depth += -1 if tag.closing else 1
            if depth == 0:
                return index
        return None

    parts: list[str | DetailsBlock] = []
    cursor = 0
    index = 0
    while index < len(tags):
        tag = tags[index]
        if tag.start < cursor or tag.name != "details" or tag.closing:
            index += 1
            continue

        close_index = matching_details_close(index)
        if close_index is None:
            break

        close_tag = tags[close_index]
        parts.append(content[cursor : tag.start])
        inner = content[tag.end : close_tag.start]
        summary, body = extract_details_summary(inner)
        parts.append(DetailsBlock(summary=summary, body=body))
        cursor = close_tag.end
        index = close_index + 1

    parts.append(content[cursor:])
    return parts


def extract_details_summary(content: str) -> tuple[str, str]:
    tags = markdown_html_tags(content)
    for index, tag in enumerate(tags):
        if tag.name == "details":
            break
        if tag.name != "summary" or tag.closing:
            continue
        close_tag = next(
            (
                candidate
                for candidate in tags[index + 1 :]
                if candidate.name == "summary" and candidate.closing
            ),
            None,
        )
        if close_tag is None:
            break
        summary = content[tag.end : close_tag.start].strip()
        body = content[: tag.start] + content[close_tag.end :]
        return summary or "Details", body.lstrip("\n")
    return "Details", content


def markdown_inline_from_html(content: str) -> str:
    content = re.sub(
        r"<code>(.*?)</code>",
        lambda match: f"`{html.unescape(re.sub(r'<[^>]+>', '', match.group(1))).replace('`', '')}`",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    content = re.sub(
        r"<(?:i|em)>(.*?)</(?:i|em)>",
        lambda match: f"_{markdown_inline_from_html(match.group(1))}_",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    content = re.sub(
        r"<(?:b|strong)>(.*?)</(?:b|strong)>",
        lambda match: f"**{markdown_inline_from_html(match.group(1))}**",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )

    def replace_link(match: re.Match) -> str:
        href = match.group("href")
        label = html.unescape(re.sub(r"<[^>]+>", "", match.group("label"))).replace(
            "`", ""
        )
        return f"[{label}]({href})"

    content = re.sub(
        r"<a\b[^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>(?P<label>.*?)</a>",
        replace_link,
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )
    content = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)
    content = re.sub(r"</?(?:span|div)\b[^>]*>", "", content, flags=re.IGNORECASE)
    return html.unescape(content)


def normalize_markdown_html_blocks(content: str) -> str:
    output = []
    list_stack = []
    in_fence = False
    for line in content.splitlines(keepends=True):
        if FENCE_START_RE.match(line):
            in_fence = not in_fence
            output.append(line)
            continue
        if in_fence:
            output.append(line)
            continue

        newline = "\n" if line.endswith("\n") else ""
        stripped = line.strip()
        lower = stripped.lower()
        if lower in {"<div>", "</div>", "<br>", "<br/>", "<br />"}:
            output.append(newline)
            continue

        if re.fullmatch(r"<ul\b[^>]*>", stripped, flags=re.IGNORECASE):
            list_stack.append({"kind": "ul", "index": 0})
            continue
        if re.fullmatch(r"</ul>", stripped, flags=re.IGNORECASE):
            if list_stack:
                list_stack.pop()
            output.append(newline)
            continue
        if re.fullmatch(r"<ol\b[^>]*>", stripped, flags=re.IGNORECASE):
            list_stack.append({"kind": "ol", "index": 0})
            continue
        if re.fullmatch(r"</ol>", stripped, flags=re.IGNORECASE):
            if list_stack:
                list_stack.pop()
            output.append(newline)
            continue

        item = re.fullmatch(
            r"<li\b[^>]*>(.*?)</li>", stripped, flags=re.IGNORECASE | re.DOTALL
        )
        if item:
            if list_stack:
                list_stack[-1]["index"] += 1
                marker = (
                    f"{list_stack[-1]['index']}."
                    if list_stack[-1]["kind"] == "ol"
                    else "-"
                )
                indent = "  " * (len(list_stack) - 1)
            else:
                marker = "-"
                indent = ""
            output.append(
                f"{indent}{marker} {markdown_inline_from_html(item.group(1))}{newline}"
            )
            continue

        output.append(markdown_inline_from_html(line))
    return "".join(output)


def pandoc_markdown_to_adoc(markdown: str, scratch: Path) -> str:
    if not markdown.strip():
        return ""
    scratch.parent.mkdir(parents=True, exist_ok=True)
    temp_md = scratch.with_suffix(".tmp.md")
    temp_adoc = scratch.with_suffix(".tmp.adoc")
    temp_md.write_text(normalize_markdown_html_blocks(markdown))
    try:
        run_command(
            [
                "pandoc",
                "-f",
                "gfm",
                "-t",
                "asciidoc",
                "--wrap=none",
                "-o",
                str(temp_adoc),
                str(temp_md),
            ],
            check=True,
        )
        content = postprocess_pandoc_adoc(temp_adoc.read_text())
    finally:
        temp_md.unlink(missing_ok=True)
        temp_adoc.unlink(missing_ok=True)

    return content


def details_summary_title(summary: str) -> str:
    summary = " ".join(summary.strip().split())
    if not summary:
        return "Details"
    if "<" in summary and ">" in summary:
        return f"+++{summary.replace('+++', '')}+++"
    return re.sub(r"`([^`]+)`", r"+\1+", markdown_inline_from_html(summary))


def convert_markdown_fragment_to_adoc(
    markdown: str, scratch: Path, depth: int = 0
) -> str:
    parts = split_markdown_details(markdown)
    if not any(isinstance(part, DetailsBlock) for part in parts):
        return pandoc_markdown_to_adoc(markdown, scratch)

    output = []
    for index, part in enumerate(parts):
        part_scratch = scratch.with_name(
            f"{scratch.stem}-{depth}-{index}{scratch.suffix}"
        )
        if isinstance(part, str):
            output.append(pandoc_markdown_to_adoc(part, part_scratch))
            continue

        delimiter = "=" * (4 + depth * 2)
        body = convert_markdown_fragment_to_adoc(
            part.body, part_scratch, depth + 1
        ).strip()
        output.append(
            "\n".join(
                [
                    f".{details_summary_title(part.summary)}",
                    "[%collapsible]",
                    delimiter,
                    body,
                    delimiter,
                    "",
                ]
            )
        )
    return "\n\n".join(block.strip() for block in output if block.strip()) + "\n"


def convert_markdown_to_adoc_content(markdown: str, title: str, scratch: Path) -> str:
    scratch.parent.mkdir(parents=True, exist_ok=True)
    content = convert_markdown_fragment_to_adoc(markdown, scratch)
    content = normalize_adoc_heading_sequence(content)
    if not content.lstrip().startswith("= "):
        content = f"= {title}\n\n{content}"
    return content


def strip_adoc_document_title(content: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if not line.startswith("= "):
            return content
        body = lines[index + 1 :]
        while body and not body[0].strip():
            body = body[1:]
        return "\n".join(body) + ("\n" if body else "")
    return content


def convert_markdown_to_adoc(markdown: str, target: Path, title: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(convert_markdown_to_adoc_content(markdown, title, target))


def convert_readme_to_overview_body(markdown: str, scratch: Path, title: str) -> str:
    return strip_adoc_document_title(
        convert_markdown_to_adoc_content(markdown, title, scratch)
    )


def legacy_readme_targets() -> dict[str, str]:
    return {
        "README.md": "index.adoc",
        "readme.md": "index.adoc",
        "./README.md": "index.adoc",
        "./readme.md": "index.adoc",
    }


def init_git_repo(repo_root: Path, message: str) -> None:
    run_command(["git", "init", "--quiet"], cwd=repo_root, check=True)
    run_command(
        ["git", "config", "user.name", "Beman Antora Docs"], cwd=repo_root, check=True
    )
    run_command(
        ["git", "config", "user.email", "beman-antora-docs@example.invalid"],
        cwd=repo_root,
        check=True,
    )
    run_command(["git", "add", "."], cwd=repo_root, check=True)
    run_command(["git", "commit", "--quiet", "-m", message], cwd=repo_root, check=True)


def build_library_docs(
    manifest: dict, repos_root: Path, clone_missing: bool, update_repos: bool
) -> list[dict]:
    libraries = []
    for repo_name, raw_config in manifest.items():
        config = raw_config or {}
        repo_path = repos_root / repo_name
        ensure_source_repo(repo_path, repo_name, clone_missing, update_repos)

        readme_source = (
            Path("README.md") if (repo_path / "README.md").exists() else None
        )
        docs = []
        for entry in config.get("files", []):
            source_rel, target_rel = parse_file_entry(entry)
            docs.append(
                {
                    "source_rel": source_rel,
                    "target_rel": target_rel,
                    "label": make_sidebar_label(target_rel.name),
                }
            )

        libraries.append(
            {
                "repo": repo_name,
                "repo_path": repo_path,
                "component": component_name(repo_name),
                "title": f"beman.{repo_name}",
                "nav_title": repo_name,
                "readme_source": readme_source,
                "docs": docs,
                "repo_url": f"https://github.com/bemanproject/{repo_name}",
                "repo_branch": "main",
                "has_api": (repo_path / "include").exists(),
            }
        )
    return libraries


def write_global_nav(libraries: list[dict], skip_api_reference: bool) -> str:
    lines = [
        "* Project",
        "** xref:beman:ROOT:index.adoc[Overview]",
        "** xref:beman:ROOT:beman_library_maturity_model.adoc[Beman Library Maturity Model]",
        "** xref:beman:ROOT:beman_standard.adoc[Beman Standard]",
        "** xref:beman:ROOT:mission.adoc[Mission]",
        "** xref:beman:ROOT:faq.adoc[FAQ]",
        "** xref:beman:ROOT:governance.adoc[Governance]",
        "** xref:beman:ROOT:code_of_conduct.adoc[Code of Conduct]",
        "* Libraries",
    ]
    for library in libraries:
        lines.append(f"** {library['nav_title']}")
        lines.append(f"*** xref:{library['component']}:ROOT:index.adoc[Overview]")
        for doc in library["docs"]:
            lines.append(
                f"*** xref:{library['component']}:ROOT:{doc['target_rel'].as_posix()}[{doc['label']}]"
            )
        if library["has_api"] and not skip_api_reference:
            lines.append(
                f"*** xref:{library['component']}:ROOT:reference/index.adoc[API Reference]"
            )
    return "\n".join(lines) + "\n"


def write_project_component(work_root: Path, global_nav: str) -> Path:
    component_root = work_root / "sources" / "beman-docs"
    pages_root = component_root / "modules" / "ROOT" / "pages"
    assets_root = component_root / "modules" / "ROOT" / "assets" / "images" / "images"
    assets_root.mkdir(parents=True, exist_ok=True)
    for source in (WEBSITE_ROOT / "static" / "images").rglob("*"):
        if source.is_file():
            target = assets_root / source.relative_to(
                WEBSITE_ROOT / "static" / "images"
            )
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for source in (WEBSITE_ROOT / "docs" / "images").rglob("*"):
        if source.is_file():
            target = assets_root / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    source_link_map = {
        source_name: target_name for source_name, target_name, _title in PROJECT_DOCS
    }
    for source_name, target_name, title in PROJECT_DOCS:
        markdown = strip_frontmatter((WEBSITE_ROOT / "docs" / source_name).read_text())
        markdown = rewrite_project_markdown_links(
            markdown, Path(source_name), source_link_map
        )
        convert_markdown_to_adoc(markdown, pages_root / target_name, title)

    write_text(component_root / "modules" / "ROOT" / "nav.adoc", global_nav)
    write_text(
        component_root / "antora.yml",
        "\n".join(
            [
                "name: beman",
                "title: Beman Project",
                "version: latest",
                "display_version: latest",
                "start_page: ROOT:index.adoc",
                "nav:",
                "  - modules/ROOT/nav.adoc",
                "",
            ]
        ),
    )
    init_git_repo(component_root, "Create Beman project Antora docs")
    return component_root


def write_mrdocs_helpers(repo_root: Path, component_title: str) -> None:
    scripts_dir = repo_root / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    wrapper = scripts_dir / "generate-antora-reference.sh"
    write_text(
        wrapper,
        "\n".join(
            [
                "#!/bin/sh",
                "set -eu",
                "if ! mrdocs docs/mrdocs.yml --generator=adoc --output=build/mrdocs-reference --ignore-failures --ignore-map-errors; then",
                "  test -f docs/build/mrdocs-reference/index.adoc",
                "fi",
                f"python3 scripts/fix-mrdocs-antora.py docs/build/mrdocs-reference --component-title {shlex.quote(component_title)}",
                "",
            ]
        ),
    )
    wrapper.chmod(0o755)
    shutil.copy2(
        WEBSITE_ROOT / "scripts" / "fix-mrdocs-antora.py",
        scripts_dir / "fix-mrdocs-antora.py",
    )


def write_library_component(
    work_root: Path, library: dict, global_nav: str, skip_api_reference: bool
) -> Path:
    staged_repo = work_root / "sources" / library["repo"]
    copy_repo(library["repo_path"], staged_repo)

    pages_root = staged_repo / "modules" / "ROOT" / "pages"
    pages_root.mkdir(parents=True, exist_ok=True)
    source_link_map = legacy_readme_targets() if library["readme_source"] else {}
    source_link_map.update(
        {
            doc["source_rel"].as_posix(): doc["target_rel"].as_posix()
            for doc in library["docs"]
        }
    )

    overview_lines = [
        f"= {library['title']}",
        "",
        f"* {library['repo_url']}[GitHub URL]",
    ]
    for doc in library["docs"]:
        overview_lines.append(f"* xref:{doc['target_rel'].as_posix()}[{doc['label']}]")
    if library["has_api"] and not skip_api_reference:
        overview_lines.append("* xref:reference/index.adoc[API Reference]")

    index_content = "\n".join(overview_lines) + "\n"
    if library["readme_source"]:
        readme_source = staged_repo / library["readme_source"]
        if readme_source.exists():
            markdown = strip_frontmatter(readme_source.read_text())
            markdown = rewrite_github_blob_image_links(markdown)
            markdown = rewrite_library_markdown_links(
                markdown,
                library["repo_url"],
                library["repo_branch"],
                source_link_map,
                library["readme_source"],
            )
            readme_body = convert_readme_to_overview_body(
                markdown, pages_root / "index-readme.adoc", library["title"]
            )
            if readme_body.strip():
                index_content += "\n" + readme_body
    write_text(pages_root / "index.adoc", index_content)

    for doc in library["docs"]:
        source = staged_repo / doc["source_rel"]
        if not source.exists():
            print(f"Missing library markdown source: {source}")
            continue
        markdown = strip_frontmatter(source.read_text())
        markdown = rewrite_github_blob_image_links(markdown)
        markdown = rewrite_library_markdown_links(
            markdown,
            library["repo_url"],
            library["repo_branch"],
            source_link_map,
            doc["source_rel"],
        )
        convert_markdown_to_adoc(markdown, pages_root / doc["target_rel"], doc["label"])

    write_text(staged_repo / "modules" / "ROOT" / "nav.adoc", global_nav)
    antora_lines = [
        f"name: {library['component']}",
        f"title: {library['title']}",
        "version: latest",
        "display_version: latest",
        "start_page: ROOT:index.adoc",
        "nav:",
        "  - modules/ROOT/nav.adoc",
    ]

    if library["has_api"] and not skip_api_reference:
        mrdocs_config = prepare_staged_mrdocs_inputs(staged_repo, library["repo"])
        if mrdocs_config.exists():
            write_mrdocs_helpers(staged_repo, library["title"])
            antora_lines.extend(
                [
                    "ext:",
                    "  collector:",
                    "    - clean:",
                    "        dir: docs/build/mrdocs-reference",
                    "      run:",
                    "        command: scripts/generate-antora-reference.sh",
                    "      scan:",
                    "        dir: docs/build/mrdocs-reference",
                    "        into: modules/ROOT/pages/reference",
                    "        files: '**/*.adoc'",
                ]
            )
        else:
            print(
                f"Skipping API reference for {library['title']}: missing {mrdocs_config}"
            )

    write_text(staged_repo / "antora.yml", "\n".join(antora_lines) + "\n")
    init_git_repo(staged_repo, f"Create {library['title']} Antora docs")
    return staged_repo


def write_supplemental_ui(work_root: Path) -> Path:
    supplemental_ui = work_root / "supplemental-ui"
    write_text(
        supplemental_ui / "partials" / "header-content.hbs",
        "\n".join(
            [
                '<header class="header site-header">',
                '  <nav class="navbar site-nav" aria-label="Main navigation">',
                '    <a class="brand" href="{{{siteRootPath}}}/../">',
                '      <img src="{{{siteRootPath}}}/../img/beman_logo.png" alt="The Beman Project Logo">',
                "      <span>The Beman Project</span>",
                "    </a>",
                '    <button class="navbar-burger site-nav-toggle" type="button" aria-controls="topbar-nav" aria-expanded="false">Menu</button>',
                '    <button class="theme-toggle theme-toggle-mobile" type="button" aria-label="Switch between dark and light mode" aria-live="polite">',
                '      <svg class="theme-toggle-icon theme-toggle-icon-light" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">',
                '        <path fill="currentColor" d="M12,9c1.65,0,3,1.35,3,3s-1.35,3-3,3s-3-1.35-3-3S10.35,9,12,9 M12,7c-2.76,0-5,2.24-5,5s2.24,5,5,5s5-2.24,5-5 S14.76,7,12,7L12,7z M2,13l2,0c0.55,0,1-0.45,1-1s-0.45-1-1-1l-2,0c-0.55,0-1,0.45-1,1S1.45,13,2,13z M20,13l2,0c0.55,0,1-0.45,1-1 s-0.45-1-1-1l-2,0c-0.55,0-1,0.45-1,1S19.45,13,20,13z M11,2v2c0,0.55,0.45,1,1,1s1-0.45,1-1V2c0-0.55-0.45-1-1-1S11,1.45,11,2z M11,20v2c0,0.55,0.45,1,1,1s1-0.45,1-1v-2c0-0.55-0.45-1-1-1C11.45,19,11,19.45,11,20z M5.99,4.58c-0.39-0.39-1.03-0.39-1.41,0 c-0.39,0.39-0.39,1.03,0,1.41l1.06,1.06c0.39,0.39,1.03,0.39,1.41,0s0.39-1.03,0-1.41L5.99,4.58z M18.36,16.95 c-0.39-0.39-1.03-0.39-1.41,0c-0.39,0.39-0.39,1.03,0,1.41l1.06,1.06c0.39,0.39,1.03,0.39,1.41,0c0.39-0.39,0.39-1.03,0-1.41 L18.36,16.95z M19.42,5.99c0.39-0.39,0.39-1.03,0-1.41c-0.39-0.39-1.03-0.39-1.41,0l-1.06,1.06c-0.39,0.39-0.39,1.03,0,1.41 s1.03,0.39,1.41,0L19.42,5.99z M7.05,18.36c0.39-0.39,0.39-1.03,0-1.41c-0.39-0.39-1.03-0.39-1.41,0l-1.06,1.06 c-0.39,0.39-0.39,1.03,0,1.41s1.03,0.39,1.41,0L7.05,18.36z"></path>',
                "      </svg>",
                '      <svg class="theme-toggle-icon theme-toggle-icon-dark" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">',
                '        <path fill="currentColor" d="M9.37,5.51C9.19,6.15,9.1,6.82,9.1,7.5c0,4.08,3.32,7.4,7.4,7.4c0.68,0,1.35-0.09,1.99-0.27C17.45,17.19,14.93,19,12,19 c-3.86,0-7-3.14-7-7C5,9.07,6.81,6.55,9.37,5.51z M12,3c-4.97,0-9,4.03-9,9s4.03,9,9,9s9-4.03,9-9c0-0.46-0.04-0.92-0.1-1.36 c-0.98,1.37-2.58,2.26-4.4,2.26c-2.98,0-5.4-2.42-5.4-5.4c0-1.81,0.89-3.42,2.26-4.4C12.92,3.04,12.46,3,12,3L12,3z"></path>',
                "      </svg>",
                "    </button>",
                '    <div class="nav-menu navbar-menu" id="topbar-nav">',
                '      <div class="nav-links navbar-end">',
                '        <a class="navbar-item" href="{{{siteRootPath}}}/../">Home</a>',
                '        <a class="navbar-item active" href="{{{siteRootPath}}}/">Docs</a>',
                '        <a class="navbar-item" href="{{{siteRootPath}}}/../libraries/">Libraries</a>',
                '        <a class="navbar-item" href="{{{siteRootPath}}}/../talks/">Talks</a>',
                '        <a class="navbar-item" href="{{{siteRootPath}}}/../blog/">Blog</a>',
                "      </div>",
                '      <div class="social-links" aria-label="Community links">',
                '        <a class="social-link discourse" href="https://discourse.bemanproject.org/" aria-label="Discourse Forum"></a>',
                '        <a class="social-link discord" href="https://discord.com/invite/BKpNyJgSbm" aria-label="Discord"></a>',
                '        <a class="social-link github" href="https://github.com/bemanproject" aria-label="GitHub Repository"></a>',
                '        <button class="theme-toggle" type="button" aria-label="Switch between dark and light mode" aria-live="polite">',
                '          <svg class="theme-toggle-icon theme-toggle-icon-light" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">',
                '            <path fill="currentColor" d="M12,9c1.65,0,3,1.35,3,3s-1.35,3-3,3s-3-1.35-3-3S10.35,9,12,9 M12,7c-2.76,0-5,2.24-5,5s2.24,5,5,5s5-2.24,5-5 S14.76,7,12,7L12,7z M2,13l2,0c0.55,0,1-0.45,1-1s-0.45-1-1-1l-2,0c-0.55,0-1,0.45-1,1S1.45,13,2,13z M20,13l2,0c0.55,0,1-0.45,1-1 s-0.45-1-1-1l-2,0c-0.55,0-1,0.45-1,1S19.45,13,20,13z M11,2v2c0,0.55,0.45,1,1,1s1-0.45,1-1V2c0-0.55-0.45-1-1-1S11,1.45,11,2z M11,20v2c0,0.55,0.45,1,1,1s1-0.45,1-1v-2c0-0.55-0.45-1-1-1C11.45,19,11,19.45,11,20z M5.99,4.58c-0.39-0.39-1.03-0.39-1.41,0 c-0.39,0.39-0.39,1.03,0,1.41l1.06,1.06c0.39,0.39,1.03,0.39,1.41,0s0.39-1.03,0-1.41L5.99,4.58z M18.36,16.95 c-0.39-0.39-1.03-0.39-1.41,0c-0.39,0.39-0.39,1.03,0,1.41l1.06,1.06c0.39,0.39,1.03,0.39,1.41,0c0.39-0.39,0.39-1.03,0-1.41 L18.36,16.95z M19.42,5.99c0.39-0.39,0.39-1.03,0-1.41c-0.39-0.39-1.03-0.39-1.41,0l-1.06,1.06c-0.39,0.39-0.39,1.03,0,1.41 s1.03,0.39,1.41,0L19.42,5.99z M7.05,18.36c0.39-0.39,0.39-1.03,0-1.41c-0.39-0.39-1.03-0.39-1.41,0l-1.06,1.06 c-0.39,0.39-0.39,1.03,0,1.41s1.03,0.39,1.41,0L7.05,18.36z"></path>',
                "          </svg>",
                '          <svg class="theme-toggle-icon theme-toggle-icon-dark" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true">',
                '            <path fill="currentColor" d="M9.37,5.51C9.19,6.15,9.1,6.82,9.1,7.5c0,4.08,3.32,7.4,7.4,7.4c0.68,0,1.35-0.09,1.99-0.27C17.45,17.19,14.93,19,12,19 c-3.86,0-7-3.14-7-7C5,9.07,6.81,6.55,9.37,5.51z M12,3c-4.97,0-9,4.03-9,9s4.03,9,9,9s9-4.03,9-9c0-0.46-0.04-0.92-0.1-1.36 c-0.98,1.37-2.58,2.26-4.4,2.26c-2.98,0-5.4-2.42-5.4-5.4c0-1.81,0.89-3.42,2.26-4.4C12.92,3.04,12.46,3,12,3L12,3z"></path>',
                "          </svg>",
                "        </button>",
                "      </div>",
                "    </div>",
                "  </nav>",
                "</header>",
                "<script>",
                "(function () {",
                "  var themeToggles = document.querySelectorAll('.theme-toggle');",
                "  function currentTheme() {",
                "    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';",
                "  }",
                "  function setTheme(theme) {",
                "    document.documentElement.setAttribute('data-theme', theme);",
                "    themeToggles.forEach(function (themeToggle) {",
                "      var label = 'Switch between dark and light mode (currently ' + theme + ' mode)';",
                "      themeToggle.setAttribute('aria-label', label);",
                "      themeToggle.setAttribute('title', label);",
                "      themeToggle.setAttribute('aria-pressed', String(theme === 'dark'));",
                "    });",
                "    try { window.localStorage.setItem('theme', theme); } catch (err) {}",
                "  }",
                "  setTheme(currentTheme());",
                "  themeToggles.forEach(function (themeToggle) {",
                "    themeToggle.addEventListener('click', function () {",
                "      setTheme(currentTheme() === 'dark' ? 'light' : 'dark');",
                "    });",
                "  });",
                "})();",
                "</script>",
                "",
            ]
        ),
    )
    write_text(
        supplemental_ui / "partials" / "footer-content.hbs",
        "\n".join(
            [
                '<footer class="site-footer">',
                "  <div>",
                "    <h2>Community</h2>",
                '    <a href="https://discord.com/invite/BKpNyJgSbm">Discord</a>',
                '    <a href="https://discourse.bemanproject.org/">Discourse</a>',
                "  </div>",
                "  <div>",
                "    <h2>More</h2>",
                '    <a href="https://github.com/bemanproject">GitHub</a>',
                "  </div>",
                "  <p>Copyright (C) The Beman Project. Built with Antora.</p>",
                "</footer>",
                "<script>",
                "(function () {",
                "  var expandedKey = 'beman.antora.nav.expanded';",
                "  var scrollKey = 'beman.antora.nav.scrollTop';",
                "  function navPanel() { return document.querySelector('.nav-panel-menu[data-panel=\"menu\"]'); }",
                "  function storage() {",
                "    try { return window.sessionStorage; } catch (err) { return null; }",
                "  }",
                "  function itemLabel(item) {",
                "    var label = item.querySelector(':scope > .nav-text, :scope > .nav-link');",
                "    return label ? label.textContent.trim() : '';",
                "  }",
                "  function itemKey(item) {",
                "    var parts = [];",
                "    var current = item;",
                "    while (current && current.classList && current.classList.contains('nav-item')) {",
                "      var label = itemLabel(current);",
                "      if (label) parts.unshift(label);",
                "      var parentList = current.parentElement;",
                "      current = parentList ? parentList.closest('.nav-item') : null;",
                "    }",
                "    return parts.join(' / ');",
                "  }",
                "  function readExpanded() {",
                "    var store = storage();",
                "    if (!store) return new Set();",
                "    try { return new Set(JSON.parse(store.getItem(expandedKey) || '[]')); } catch (err) { return new Set(); }",
                "  }",
                "  function writeExpanded() {",
                "    var panel = navPanel();",
                "    var store = storage();",
                "    if (!panel || !store) return;",
                "    var keys = [];",
                "    panel.querySelectorAll('.nav-item.is-active').forEach(function (item) {",
                "      var key = itemKey(item);",
                "      if (key) keys.push(key);",
                "    });",
                "    try { store.setItem(expandedKey, JSON.stringify(keys)); } catch (err) {}",
                "  }",
                "  function expandAncestors(item) {",
                "    var current = item;",
                "    while (current) {",
                "      if (current.classList && current.classList.contains('nav-item')) current.classList.add('is-active', 'is-current-path');",
                "      var parentList = current.parentElement;",
                "      current = parentList ? parentList.closest('.nav-item') : null;",
                "    }",
                "  }",
                "  function apiReferenceInfo() {",
                "    var segments = window.location.pathname.split('/').filter(Boolean);",
                "    for (var index = 0; index < segments.length - 2; index += 1) {",
                "      if (!segments[index].startsWith('beman.')) continue;",
                "      if (segments[index + 2] !== 'reference') continue;",
                "      var baseSegments = segments.slice(0, index + 3);",
                "      var tail = segments.slice(index + 3);",
                "      return {",
                "        component: segments[index],",
                "        componentLabel: segments[index].replace(/^beman\\./, ''),",
                "        version: segments[index + 1],",
                "        tail: tail,",
                "        componentPath: '/' + segments.slice(0, index + 2).join('/') + '/index.html',",
                "        indexPath: '/' + baseSegments.join('/') + '/index.html'",
                "      };",
                "    }",
                "    return null;",
                "  }",
                "  function normalizePath(path) {",
                "    return path.replace(/\\/$/, '/index.html');",
                "  }",
                "  function apiReferenceNavLink(info, panel) {",
                "    if (!info || !panel) return null;",
                "    var referencePrefix = info.indexPath.replace(/index\\.html$/, '');",
                "    var match = null;",
                "    panel.querySelectorAll('.nav-link').forEach(function (link) {",
                "      if (match || link.textContent.trim() !== 'API Reference') return;",
                "      var linkPath = normalizePath(new URL(link.getAttribute('href'), window.location.href).pathname);",
                "      if (linkPath.startsWith(referencePrefix)) match = link;",
                "    });",
                "    return match;",
                "  }",
                "  function markApiReferenceNav(panel) {",
                "    var info = apiReferenceInfo();",
                "    if (!info || !panel) return null;",
                "    var link = apiReferenceNavLink(info, panel);",
                "    var match = link ? link.closest('.nav-item') : null;",
                "    if (link) link.classList.add('is-current-page');",
                "    if (match) {",
                "      match.classList.add('is-current-page', 'is-current-path');",
                "      expandAncestors(match);",
                "    }",
                "    return match;",
                "  }",
                "  function ensureNavItemVisible(panel, item) {",
                "    if (!panel || !item) return;",
                "    window.setTimeout(function () {",
                "      var itemTop = item.offsetTop;",
                "      var itemBottom = itemTop + item.offsetHeight;",
                "      var panelBottom = panel.scrollTop + panel.clientHeight;",
                "      if (itemTop < panel.scrollTop || itemBottom > panelBottom) {",
                "        panel.scrollTop = Math.max(0, itemTop - panel.clientHeight / 3);",
                "        saveScroll();",
                "      }",
                "    }, 0);",
                "  }",
                "  function expandRequiredSections(panel) {",
                "    panel.querySelectorAll('.nav-item').forEach(function (item) {",
                "      var label = itemLabel(item);",
                "      if (label === 'Project' || label === 'Libraries') item.classList.add('is-active');",
                "    });",
                "    panel.querySelectorAll('.nav-item.is-current-page, .nav-item.is-current-path').forEach(expandAncestors);",
                "    markApiReferenceNav(panel);",
                "  }",
                "  function restoreExpanded(panel) {",
                "    var expanded = readExpanded();",
                "    panel.querySelectorAll('.nav-item').forEach(function (item) {",
                "      if (expanded.has(itemKey(item))) item.classList.add('is-active');",
                "    });",
                "    expandRequiredSections(panel);",
                "  }",
                "  function restoreScroll(panel) {",
                "    var store = storage();",
                "    if (!store) return;",
                "    try {",
                "      var saved = parseInt(store.getItem(scrollKey) || '', 10);",
                "      if (!Number.isNaN(saved)) panel.scrollTop = saved;",
                "    } catch (err) {}",
                "  }",
                "  function saveScroll() {",
                "    var panel = navPanel();",
                "    var store = storage();",
                "    if (!panel || !store) return;",
                "    try { store.setItem(scrollKey, String(panel.scrollTop)); } catch (err) {}",
                "  }",
                "  function articleScroller() {",
                "    var article = document.querySelector('article.doc');",
                "    if (!article) return null;",
                "    var style = window.getComputedStyle(article);",
                "    if (style.overflowY === 'visible' || article.scrollHeight <= article.clientHeight + 1) return null;",
                "    return article;",
                "  }",
                "  function scrollArticleToHash(hash, mode) {",
                "    if (!hash || hash.charAt(0) !== '#') return false;",
                "    var article = articleScroller();",
                "    if (!article) return false;",
                "    var id = hash.slice(1);",
                "    try { id = decodeURIComponent(id); } catch (err) {}",
                "    var target = document.getElementById(id);",
                "    if (!target || !article.contains(target)) return false;",
                "    var targetTop = target.getBoundingClientRect().top - article.getBoundingClientRect().top + article.scrollTop;",
                "    article.scrollTo({ top: Math.max(0, targetTop - 8), behavior: mode || 'auto' });",
                "    window.scrollTo(0, 0);",
                "    return true;",
                "  }",
                "  function setActiveTocLink(link) {",
                "    document.querySelectorAll('.toc a.is-active').forEach(function (activeLink) {",
                "      activeLink.classList.remove('is-active');",
                "    });",
                "    link.classList.add('is-active');",
                "  }",
                "  function installAnchorScrolling() {",
                "    document.querySelectorAll('main.article a[href^=\"#\"]').forEach(function (link) {",
                "      link.addEventListener('click', function (event) {",
                "        var hash = link.getAttribute('href');",
                "        if (!scrollArticleToHash(hash, 'smooth')) return;",
                "        event.preventDefault();",
                "        if (link.closest('aside.toc')) setActiveTocLink(link);",
                "        if (window.location.hash !== hash) window.history.pushState(null, '', hash);",
                "      });",
                "    });",
                "    if (window.location.hash) window.setTimeout(function () { scrollArticleToHash(window.location.hash, 'auto'); }, 0);",
                "    window.addEventListener('hashchange', function () { scrollArticleToHash(window.location.hash, 'auto'); });",
                "  }",
                "  function installApiReferenceContext() {",
                "    var info = apiReferenceInfo();",
                "    if (!info) return;",
                "    var article = document.querySelector('article.doc');",
                "    if (!article || article.querySelector('.api-context')) return;",
                "    var anchor = article.querySelector('h1.page, h1, h2, .sect1, .paragraph, .listingblock, table') || article.firstElementChild;",
                "    var nav = document.createElement('nav');",
                "    nav.className = 'api-context';",
                "    nav.setAttribute('aria-label', 'API reference context');",
                "    var crumbs = document.createElement('ol');",
                "    crumbs.className = 'api-breadcrumbs';",
                "    function addCrumb(label, href) {",
                "      var item = document.createElement('li');",
                "      if (href) {",
                "        var link = document.createElement('a');",
                "        link.href = href;",
                "        link.textContent = label;",
                "        item.appendChild(link);",
                "      } else {",
                "        item.textContent = label;",
                "        item.setAttribute('aria-current', 'page');",
                "      }",
                "      crumbs.appendChild(item);",
                "    }",
                "    function pathLabel() {",
                "      var parts = info.tail.map(function (segment) {",
                "        var label = segment.replace(/\\.html$/, '');",
                "        try { label = decodeURIComponent(label); } catch (err) {}",
                "        return label;",
                "      }).filter(Boolean);",
                "      return parts.length ? parts.join('::') : 'API Reference';",
                "    }",
                "    function operatorLabel() {",
                "      var operators = {",
                "        operator_3way: '<=>', operator_assign: '=', operator_bitor: '|', operator_call: '()',",
                "        operator_eq: '==', operator_ge: '>=', operator_gt: '>', operator_le: '<=',",
                "        operator_lt: '<', operator_minus: '-', operator_not_eq: '!=', operator_plus: '+',",
                "        operator_ptr: '->', operator_star: '*', operator_subs: '[]'",
                "      };",
                "      var parts = info.tail.map(function (segment) {",
                "        var label = segment.replace(/\\.html$/, '').replace(/-[0-9a-f]+$/, '');",
                "        try { label = decodeURIComponent(label); } catch (err) {}",
                "        return label;",
                "      }).filter(Boolean);",
                "      var name = parts[parts.length - 1];",
                "      if (!Object.prototype.hasOwnProperty.call(operators, name)) return null;",
                "      parts[parts.length - 1] = 'operator' + operators[name];",
                "      return parts.join('::');",
                "    }",
                "    function pageLabel() {",
                "      var heading = article.querySelector('h1.page, h1');",
                "      if (!heading) return pathLabel();",
                "      var label = heading.textContent.replace(/\\s+/g, ' ').trim();",
                "      return label || pathLabel();",
                "    }",
                "    var apiLink = apiReferenceNavLink(info, navPanel());",
                "    var apiHref = apiLink ? apiLink.href : info.indexPath;",
                "    var apiPath = normalizePath(new URL(apiHref, window.location.href).pathname);",
                "    var isApiLandingPage = normalizePath(window.location.pathname) === apiPath;",
                "    addCrumb(info.componentLabel, info.componentPath);",
                "    addCrumb('API Reference', isApiLandingPage ? null : apiHref);",
                "    if (!isApiLandingPage) addCrumb(operatorLabel() || pageLabel(), null);",
                "    nav.appendChild(crumbs);",
                "    if (anchor) article.insertBefore(nav, anchor);",
                "    else article.appendChild(nav);",
                "  }",
                "  function install() {",
                "    var panel = navPanel();",
                "    if (panel) {",
                "      restoreExpanded(panel);",
                "      restoreScroll(panel);",
                "      ensureNavItemVisible(panel, markApiReferenceNav(panel));",
                "      panel.addEventListener('click', function () { window.setTimeout(writeExpanded, 0); });",
                "      panel.addEventListener('scroll', saveScroll, { passive: true });",
                "    }",
                "    installApiReferenceContext();",
                "    installAnchorScrolling();",
                "    window.addEventListener('beforeunload', function () { writeExpanded(); saveScroll(); });",
                "  }",
                "  if (document.readyState === 'complete') install();",
                "  else window.addEventListener('load', install);",
                "})();",
                "</script>",
                "",
            ]
        ),
    )
    write_text(
        supplemental_ui / "partials" / "head-styles.hbs",
        "\n".join(
            [
                "    <script>",
                "      (function () {",
                "        function getStoredTheme() {",
                "          try { return window.localStorage.getItem('theme'); } catch (err) { return null; }",
                "        }",
                "        var storedTheme = getStoredTheme();",
                "        var theme = storedTheme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');",
                "        document.documentElement.setAttribute('data-theme', theme);",
                "      })();",
                "    </script>",
                '    <link rel="stylesheet" href="{{{uiRootPath}}}/css/site.css">',
                '    <link rel="stylesheet" href="{{{uiRootPath}}}/css/beman-docs.css?v=12">',
                "",
            ]
        ),
    )
    write_text(
        supplemental_ui / "css" / "beman-docs.css",
        "\n".join(
            [
                ":root {",
                "  --ifm-color-primary: #2e8555;",
                "  --ifm-color-primary-dark: #29784c;",
                "  --ifm-color-content: #1c1e21;",
                "  --ifm-color-content-secondary: #525860;",
                "  --ifm-color-emphasis-100: #f5f6f7;",
                "  --ifm-color-emphasis-200: #ebedf0;",
                "  --ifm-color-emphasis-300: #dadde1;",
                "  --ifm-background-color: #fff;",
                "  --ifm-background-surface-color: #fff;",
                "  --beman-header-background: rgba(255, 255, 255, 0.97);",
                "  --beman-code-background: #f6f8fa;",
                "  --beman-code-color: #1c1e21;",
                "  --beman-code-link-background: #f5f6f7;",
                "  --beman-syntax-comment: #6a737d;",
                "  --beman-syntax-keyword: #d73a49;",
                "  --beman-syntax-literal: #005cc5;",
                "  --beman-syntax-string: #032f62;",
                "  --beman-syntax-title: #6f42c1;",
                "  --beman-syntax-type: #22863a;",
                "  --beman-syntax-meta: #6a737d;",
                "  --beman-footer-background: #303846;",
                "  --beman-footer-color: #fff;",
                "  --beman-footer-muted: rgba(255, 255, 255, 0.8);",
                "  --page-max: 1320px;",
                "  --content-max: 900px;",
                "  --nav-height: 60px;",
                "  --body-font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;",
                "  color-scheme: light;",
                "}",
                "html[data-theme='dark'] {",
                "  --ifm-color-primary: #5fc98b;",
                "  --ifm-color-primary-dark: #4fb77a;",
                "  --ifm-color-content: #e7e9ed;",
                "  --ifm-color-content-secondary: #a9b0ba;",
                "  --ifm-color-emphasis-100: #1b222b;",
                "  --ifm-color-emphasis-200: #303946;",
                "  --ifm-color-emphasis-300: #46515f;",
                "  --ifm-background-color: #101418;",
                "  --ifm-background-surface-color: #151a20;",
                "  --beman-header-background: rgba(16, 20, 24, 0.97);",
                "  --beman-code-background: #1b222b;",
                "  --beman-code-color: #e7e9ed;",
                "  --beman-code-link-background: #202a36;",
                "  --beman-syntax-comment: #8b949e;",
                "  --beman-syntax-keyword: #ff7b72;",
                "  --beman-syntax-literal: #79c0ff;",
                "  --beman-syntax-string: #a5d6ff;",
                "  --beman-syntax-title: #d2a8ff;",
                "  --beman-syntax-type: #7ee787;",
                "  --beman-syntax-meta: #8b949e;",
                "  --beman-footer-background: #111820;",
                "  --beman-footer-color: #e7e9ed;",
                "  --beman-footer-muted: rgba(231, 233, 237, 0.72);",
                "  color-scheme: dark;",
                "}",
                "",
                "*, *::before, *::after { box-sizing: border-box; }",
                "html { scrollbar-gutter: stable; }",
                "",
                "body.article {",
                "  display: flex;",
                "  flex-direction: column;",
                "  height: 100dvh;",
                "  min-height: 100vh;",
                "  margin: 0;",
                "  padding-top: 0;",
                "  overflow: hidden;",
                "  color: var(--ifm-color-content);",
                "  font-family: var(--body-font-family);",
                "  font-size: 16px;",
                "  line-height: 1.65;",
                "  background: var(--ifm-background-color);",
                "}",
                "",
                "a { color: var(--ifm-color-primary); text-decoration: none; }",
                "a:hover { text-decoration: underline; }",
                "",
                ".site-header.header {",
                "  display: block;",
                "  flex: 0 0 var(--nav-height);",
                "  position: static;",
                "  top: 0;",
                "  z-index: 20;",
                "  height: var(--nav-height);",
                "  border-bottom: 1px solid var(--ifm-color-emphasis-200);",
                "  background: var(--beman-header-background);",
                "  box-shadow: none;",
                "}",
                ".site-nav.navbar {",
                "  display: flex;",
                "  position: static;",
                "  align-items: center;",
                "  max-width: var(--page-max);",
                "  height: 100%;",
                "  min-height: 0;",
                "  margin: 0 auto;",
                "  padding: 0 16px;",
                "  gap: 16px;",
                "  background: transparent;",
                "}",
                ".brand {",
                "  display: inline-flex;",
                "  align-items: center;",
                "  gap: 9.6px;",
                "  color: var(--ifm-color-content);",
                "  font-weight: 700;",
                "  line-height: 26.4px;",
                "  white-space: nowrap;",
                "}",
                ".brand:hover { text-decoration: none; }",
                ".brand img { width: 32px; height: 32px; }",
                ".nav-menu.navbar-menu {",
                "  display: flex;",
                "  position: static;",
                "  align-items: center;",
                "  justify-content: space-between;",
                "  flex: 1;",
                "  height: auto;",
                "  min-height: 0;",
                "  min-width: 0;",
                "  padding: 0;",
                "  background: transparent;",
                "  box-shadow: none;",
                "}",
                ".nav-links { display: flex; align-items: center; gap: 3.2px; }",
                ".nav-links.navbar-end { margin-left: 0; margin-right: 0; }",
                ".nav-links a.navbar-item {",
                "  display: block;",
                "  flex: none;",
                "  padding: 7.2px 12px;",
                "  border-radius: 4px;",
                "  color: var(--ifm-color-content);",
                "  font-weight: 500;",
                "  line-height: 26.4px;",
                "}",
                ".nav-links a.navbar-item:hover, .nav-links a.navbar-item.active {",
                "  color: var(--ifm-color-primary);",
                "  text-decoration: none;",
                "  background: transparent;",
                "}",
                ".social-links {",
                "  display: flex;",
                "  align-items: center;",
                "  gap: 5.6px;",
                "}",
                ".social-link {",
                "  width: 32px;",
                "  height: 32px;",
                "  padding: 6px;",
                "  border-radius: 50%;",
                "  background-position: center;",
                "  background-repeat: no-repeat;",
                "  background-size: 20px 20px;",
                "  transition: background-color 120ms ease;",
                "}",
                ".social-link:hover { background-color: var(--ifm-color-emphasis-200); }",
                ".social-link.discourse {",
                "  background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cpath fill='%230055A5' d='M128 0C57.3 0 0 57.3 0 128s57.3 128 128 128c27.7 0 54-8.5 75.5-24.6l-34.5-36.5C153.5 207.6 141 211 128 211c-45.9 0-83.2-37.3-83.2-83.2S82.1 44.6 128 44.6s83.2 37.3 83.2 83.2v.4c0 22.3-8.6 43-24.2 58.6L256 255.9C239.3 238.5 245.9 243.8 256 255.9v-128C256 57.3 198.7 0 128 0z'/%3E%3C/svg%3E\");",
                "}",
                ".social-link.discord {",
                "  background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 127.14 96.36'%3E%3Cpath fill='%235865F2' d='M107.7,8.07A105.15,105.15,0,0,0,81.47,0a72.06,72.06,0,0,0-3.36,6.83A97.68,97.68,0,0,0,49,6.83,72.37,72.37,0,0,0,45.64,0,105.89,105.89,0,0,0,19.39,8.09C2.79,32.65-1.71,56.6.54,80.21h0A105.73,105.73,0,0,0,32.71,96.36,77.11,77.11,0,0,0,39.6,85.25a68.42,68.42,0,0,1-10.85-5.18c.91-.66,1.8-1.34,2.66-2a75.57,75.57,0,0,0,64.32,0c.87.71,1.76,1.39,2.66,2a68.68,68.68,0,0,1-10.87,5.19,77,77,0,0,0,6.89,11.1A105.25,105.25,0,0,0,126.6,80.22c1.24-23.25-1.52-47.56-18.9-72.15ZM42.45,65.69C36.18,65.69,31,60,31,53s5-12.74,11.43-12.74S54,46,53.89,53,48.84,65.69,42.45,65.69Zm42.24,0C78.41,65.69,73.25,60,73.25,53s5-12.74,11.44-12.74S96.23,46,96.12,53,91.08,65.69,84.69,65.69Z'/%3E%3C/svg%3E\");",
                "}",
                ".social-link.github {",
                "  margin-right: 6.4px;",
                "  background-image: url(\"data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='%231c1e21' d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/%3E%3C/svg%3E\");",
                "}",
                "html[data-theme='dark'] .social-link.github {",
                "  background-image: url(\"data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath fill='white' d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/%3E%3C/svg%3E\");",
                "}",
                ".theme-toggle {",
                "  display: inline-flex;",
                "  align-items: center;",
                "  justify-content: center;",
                "  width: 32px;",
                "  height: 32px;",
                "  border: 0;",
                "  border-radius: 50%;",
                "  padding: 0;",
                "  background: transparent;",
                "  color: var(--ifm-color-content);",
                "  cursor: pointer;",
                "  transition: background-color 120ms ease;",
                "}",
                ".theme-toggle:hover { background-color: var(--ifm-color-emphasis-200); }",
                ".theme-toggle-icon { width: 24px; height: 24px; }",
                ".theme-toggle-mobile { display: none; }",
                "html[data-theme='light'] .theme-toggle-icon-dark, html[data-theme='dark'] .theme-toggle-icon-light { display: none; }",
                ".site-nav-toggle {",
                "  display: none;",
                "  flex: 0 0 auto;",
                "  margin-left: auto;",
                "  border: 1px solid var(--ifm-color-emphasis-300);",
                "  border-radius: 4px;",
                "  background: var(--ifm-background-surface-color);",
                "  padding: 5.6px 9.6px;",
                "  color: var(--ifm-color-content);",
                "  font: inherit;",
                "  line-height: 1.4;",
                "  min-width: 72px;",
                "  text-align: center;",
                "  white-space: nowrap;",
                "}",
                "",
                ".body {",
                "  display: grid;",
                "  grid-template-columns: minmax(210px, 260px) minmax(0, var(--content-max)) minmax(160px, 220px);",
                "  gap: 2rem;",
                "  flex: 1 1 auto;",
                "  max-width: var(--page-max);",
                "  width: 100%;",
                "  min-height: 0;",
                "  margin: 0 auto;",
                "  padding: 1rem;",
                "  overflow: hidden;",
                "}",
                ".nav-container { position: static; width: auto; min-height: 0; grid-column: 1; }",
                ".nav-container .nav {",
                "  position: static;",
                "  height: 100%;",
                "  max-height: none;",
                "  width: auto;",
                "  overflow: auto;",
                "  background: transparent;",
                "  color: var(--ifm-color-content-secondary);",
                "  font-size: 0.88rem;",
                "}",
                ".nav-container .panels { display: block; }",
                ".nav-panel-menu { display: block; position: static; visibility: visible; transform: none; }",
                ".nav-panel-explore { display: none; }",
                ".nav-menu .title { display: none; }",
                ".nav-list { list-style: none; margin: 0; padding: 0; }",
                ".nav-list .nav-list { margin-left: 0.75rem; padding-left: 0.75rem; border-left: 1px solid var(--ifm-color-emphasis-200); }",
                ".nav-item { margin: 0.15rem 0; }",
                ".nav-link, .nav-text {",
                "  display: block;",
                "  padding: 0.2rem 1.25rem 0.2rem 0;",
                "  color: var(--ifm-color-content-secondary);",
                "  line-height: 1.45;",
                "}",
                ".nav-text { font-weight: 600; }",
                ".nav-link:hover, .nav-item.is-current-page > .nav-link, .nav-item.is-current-path > .nav-link, .nav-item.is-current-path > .nav-text {",
                "  color: var(--ifm-color-primary);",
                "  font-weight: 600;",
                "  text-decoration: none;",
                "}",
                ".nav-item-toggle {",
                "  top: 0.25rem;",
                "  right: 0;",
                "  width: 1rem;",
                "  height: 1rem;",
                "}",
                ".nav-item-toggle::before { background: var(--ifm-color-content-secondary); }",
                ".nav-menu-toggle { display: none !important; }",
                "",
                "main.article { grid-column: 2 / 4; min-width: 0; min-height: 0; overflow: hidden; padding: 0; }",
                "main.article > .content {",
                "  display: grid;",
                "  grid-template-columns: minmax(0, var(--content-max)) minmax(180px, 220px);",
                "  gap: 2rem;",
                "  align-items: start;",
                "  height: 100%;",
                "  min-height: 0;",
                "  max-width: none;",
                "  overflow: hidden;",
                "  padding: 0;",
                "}",
                "article.doc { grid-column: 1; grid-row: 1; min-width: 0; max-width: none; height: 100%; overflow-x: hidden; overflow-y: auto; padding-right: 0.5rem; color: var(--ifm-color-content); scrollbar-gutter: stable; }",
                "article.doc .api-context { display: flex; flex-wrap: wrap; align-items: center; gap: 0.35rem 0.75rem; margin: 0 0 1rem; padding: 0; color: var(--ifm-color-content-secondary); font-size: 0.9rem; font-weight: 600; }",
                "article.doc .api-breadcrumbs { display: flex; flex-wrap: wrap; align-items: center; gap: 0.25rem 0.45rem; list-style: none; margin: 0; padding: 0; min-width: 0; }",
                "article.doc .api-breadcrumbs li { display: inline-flex; align-items: center; min-width: 0; margin: 0; padding: 0; }",
                "article.doc .api-breadcrumbs li + li::before { content: '/'; margin-right: 0.45rem; color: var(--ifm-color-content-secondary); opacity: 0.7; }",
                "article.doc .api-breadcrumbs a { color: var(--ifm-color-primary); text-decoration: none; }",
                "article.doc .api-breadcrumbs a:hover { color: var(--ifm-color-primary-dark); text-decoration: underline; }",
                "article.doc .api-breadcrumbs [aria-current='page'] { color: var(--ifm-color-content-secondary); overflow-wrap: anywhere; }",
                "article.doc h1.page:first-child { margin-top: 0; }",
                "article.doc h1, article.doc h2, article.doc h3, article.doc h4, article.doc h5, article.doc h6 { color: var(--ifm-color-content); }",
                "article.doc h1.sect0 { background: var(--ifm-color-emphasis-100); }",
                "article.doc h2:not(.discrete) { border-bottom-color: var(--ifm-color-emphasis-300); }",
                "article.doc p, article.doc li { overflow-wrap: anywhere; }",
                "article.doc a { color: var(--ifm-color-primary); }",
                "article.doc a:hover { color: var(--ifm-color-primary-dark); }",
                "article.doc a.unresolved { color: #ff7b72; }",
                "article.doc code {",
                "  padding: 0.1rem 0.25rem;",
                "  border-radius: 4px;",
                "  background: var(--ifm-color-emphasis-100);",
                "  color: var(--beman-code-color);",
                "  font-size: 0.92em;",
                "  overflow-wrap: anywhere;",
                "}",
                "article.doc a code {",
                "  background: var(--beman-code-link-background);",
                "  color: var(--ifm-color-primary);",
                "}",
                "article.doc img { max-width: 100%; height: auto; }",
                "article.doc .listingblock, article.doc .literalblock, article.doc .listingblock > .content {",
                "  width: 100%;",
                "  max-width: 100%;",
                "  min-width: 0;",
                "}",
                "article.doc pre {",
                "  display: block;",
                "  width: 100%;",
                "  max-width: 100%;",
                "  min-width: 0;",
                "  overflow-x: auto;",
                "  border-radius: 6px;",
                "  background: var(--beman-code-background);",
                "  color: var(--beman-code-color);",
                "}",
                "article.doc pre > code { display: block; min-width: max-content; }",
                "article.doc .listingblock pre:not(.highlight), article.doc .literalblock pre {",
                "  background: var(--beman-code-background);",
                "  color: var(--beman-code-color);",
                "  box-shadow: inset 0 0 1.75px var(--ifm-color-emphasis-300);",
                "}",
                "article.doc pre.highlight > code, article.doc code.hljs {",
                "  background: var(--beman-code-background);",
                "  color: var(--beman-code-color);",
                "  box-shadow: inset 0 0 1.75px var(--ifm-color-emphasis-300);",
                "}",
                "article.doc pre.highlight > code a, article.doc pre.highlight > code a code {",
                "  background: transparent;",
                "  color: var(--ifm-color-primary);",
                "}",
                "article.doc .hljs-comment, article.doc .hljs-quote { color: var(--beman-syntax-comment); }",
                "article.doc .hljs-keyword, article.doc .hljs-selector-tag, article.doc .hljs-subst { color: var(--beman-syntax-keyword); }",
                "article.doc .hljs-literal, article.doc .hljs-number, article.doc .hljs-variable, article.doc .hljs-template-variable { color: var(--beman-syntax-literal); }",
                "article.doc .hljs-string, article.doc .hljs-doctag { color: var(--beman-syntax-string); }",
                "article.doc .hljs-section, article.doc .hljs-selector-id, article.doc .hljs-title { color: var(--beman-syntax-title); }",
                "article.doc .hljs-type, article.doc .hljs-class .hljs-title { color: var(--beman-syntax-type); }",
                "article.doc .hljs-meta { color: var(--beman-syntax-meta); }",
                "article.doc table.tableblock { display: block; width: 100%; overflow-x: auto; border-collapse: collapse; }",
                "article.doc table.tableblock, article.doc table.tableblock > * > tr > * { border-color: var(--ifm-color-emphasis-300); }",
                "article.doc th, article.doc td { border-color: var(--ifm-color-emphasis-300); color: var(--ifm-color-content); }",
                "article.doc p.tableblock { color: var(--ifm-color-content); }",
                "article.doc table.stripes-all > tbody > tr, article.doc table.stripes-even > tbody > tr:nth-of-type(2n), article.doc table.stripes-hover > tbody > tr:hover, article.doc table.stripes-odd > tbody > tr:nth-of-type(odd) { background: var(--ifm-color-emphasis-100); }",
                "article.doc table.tableblock > tfoot { background: var(--ifm-color-emphasis-100); }",
                "article.doc .admonitionblock td.content, #preamble .abstract blockquote { background: var(--ifm-color-emphasis-100); color: var(--ifm-color-content); border-color: var(--ifm-color-emphasis-300); }",
                "article.doc .quoteblock, article.doc .verseblock { background: var(--ifm-color-emphasis-100); border-left-color: var(--ifm-color-emphasis-300); color: var(--ifm-color-content-secondary); }",
                "article.doc .quoteblock .attribution { color: var(--ifm-color-content-secondary); }",
                "article.doc .admonitionblock .title, article.doc .exampleblock .title, article.doc .imageblock .title, article.doc .listingblock .title, article.doc .literalblock .title, article.doc .openblock .title, article.doc .videoblock .title, article.doc table.tableblock caption, article.doc details.result > summary { color: var(--ifm-color-content-secondary); }",
                "article.doc .exampleblock > .content, article.doc details.result > .content { background: var(--ifm-background-surface-color); border-color: var(--ifm-color-emphasis-300); color: var(--ifm-color-content); }",
                "article.doc .sidebarblock { background: var(--ifm-color-emphasis-100); color: var(--ifm-color-content); }",
                "article.doc hr, nav.pagination { border-color: var(--ifm-color-emphasis-300); }",
                "article.doc kbd { background: var(--ifm-color-emphasis-100); border-color: var(--ifm-color-emphasis-300); box-shadow: 0 1px 0 var(--ifm-color-emphasis-300), inset 0 0 0 0.1em var(--ifm-background-surface-color); color: var(--ifm-color-content); }",
                "nav.pagination span::before, nav.pagination a::before, nav.pagination a::after { color: var(--ifm-color-content-secondary); }",
                ".toc-menu, .toc .toc-menu h3, .toc .toc-menu a.is-active { color: var(--ifm-color-content); }",
                ".toc .toc-menu a { border-left-color: var(--ifm-color-emphasis-300); }",
                ".toc .toc-menu a:hover { color: var(--ifm-color-primary); }",
                ".toc .toc-menu a.is-active { border-left-color: var(--ifm-color-primary); }",
                ".sidebar.toc .toc-menu a:focus { background: var(--ifm-color-emphasis-100); }",
                ".toolbar { display: none; }",
                "",
                "aside.toc.sidebar {",
                "  position: static;",
                "  grid-column: 2;",
                "  grid-row: 1;",
                "  height: 100%;",
                "  max-height: none;",
                "  width: auto;",
                "  min-width: 0;",
                "  overflow: auto;",
                "  color: var(--ifm-color-content-secondary);",
                "  font-size: 0.88rem;",
                "}",
                ".toc-menu h3 { margin-top: 0; color: var(--ifm-color-content); font-size: 0.9rem; }",
                ".toc-menu ul { list-style: none; margin: 0; padding: 0; }",
                ".toc-menu a { color: var(--ifm-color-content-secondary); }",
                ".toc-menu a.is-active, .toc-menu a:hover { color: var(--ifm-color-primary); text-decoration: none; }",
                "",
                ".site-footer {",
                "  display: none;",
                "  grid-template-columns: repeat(2, minmax(0, 180px)) 1fr;",
                "  gap: 1.5rem;",
                "  margin: 0;",
                "  padding: 2rem max(1rem, calc((100vw - var(--page-max)) / 2 + 1rem));",
                "  background: var(--beman-footer-background);",
                "  color: var(--beman-footer-color);",
                "}",
                ".site-footer h2 { margin: 0 0 0.5rem; font-size: 1rem; color: var(--beman-footer-color); }",
                ".site-footer a { display: block; color: var(--beman-footer-color); }",
                ".site-footer p { align-self: end; justify-self: end; margin: 0; color: var(--beman-footer-muted); }",
                "",
                "@media (max-width: 1100px) {",
                "  .body { grid-template-columns: minmax(190px, 240px) minmax(0, 1fr); }",
                "  main.article { grid-column: 2; }",
                "  main.article > .content { display: block; overflow: hidden; }",
                "  aside.toc.sidebar { display: none; }",
                "}",
                "@media (max-width: 760px) {",
                "  body.article { height: auto; min-height: 100vh; overflow: auto; }",
                "  .site-header.header { flex: none; height: auto; }",
                "  .site-nav.navbar { position: relative; flex-wrap: wrap; gap: 0.75rem; min-height: var(--nav-height); }",
                "  .site-nav-toggle { display: inline-block; }",
                "  .theme-toggle-mobile { display: inline-flex; }",
                "  .nav-menu.navbar-menu { display: none; position: absolute; top: calc(100% + 1px); left: 1rem; right: 1rem; z-index: 40; flex-direction: column; align-items: stretch; max-height: calc(100vh - var(--nav-height) - 1rem); padding: 0.75rem 1rem 1rem; border: 1px solid var(--ifm-color-emphasis-200); border-radius: 6px; background: var(--beman-header-background); box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22); overflow: auto; }",
                "  .nav-menu.navbar-menu.is-active { display: flex; }",
                "  .nav-links { align-items: stretch; flex-direction: column; width: 100%; margin-left: 0; }",
                "  .social-links { align-items: stretch; flex-direction: row; margin-top: 0.5rem; }",
                "  .nav-menu .theme-toggle { display: none; }",
                "  .body { display: block; position: relative; min-height: 0; overflow: visible; padding-top: 1.25rem; }",
                "  .toolbar { display: flex; position: static; height: auto; margin-bottom: 1rem; padding: 0; background: transparent; box-shadow: none; }",
                "  .toolbar .home-link, .toolbar .breadcrumbs, .toolbar .edit-this-page { display: none; }",
                "  .toolbar .nav-toggle { display: inline-flex; align-items: center; justify-content: space-between; width: 100%; min-height: 2.75rem; margin: 0; padding: 0.65rem 0.85rem; border: 1px solid var(--ifm-color-emphasis-300); border-radius: 6px; background: var(--ifm-background-surface-color); color: var(--ifm-color-content); font-weight: 600; }",
                "  .toolbar .nav-toggle::before { content: 'Docs navigation'; }",
                "  .toolbar .nav-toggle::after { content: ''; width: 0.55rem; height: 0.55rem; border-right: 2px solid currentColor; border-bottom: 2px solid currentColor; transform: rotate(45deg); transition: transform 0.15s ease; }",
                "  .toolbar .nav-toggle.is-active::after { transform: rotate(-135deg); }",
                "  .nav-container { display: none; position: absolute; top: calc(1.25rem + 2.75rem + 0.75rem); left: 1rem; right: 1rem; z-index: 30; width: auto; margin-bottom: 0; visibility: visible; }",
                "  .nav-container.is-active { display: block; }",
                "  .nav-container .nav { height: auto !important; max-height: min(70vh, 34rem); margin-bottom: 0; padding: 0.75rem 0 1rem; border: 1px solid var(--ifm-color-emphasis-200); border-radius: 6px; background: var(--ifm-background-surface-color); overflow: auto; }",
                "  .nav-container .panels { height: auto; }",
                "  .nav-panel-menu { overflow: visible; }",
                "  .nav-menu { min-height: 0; padding: 0 1rem; }",
                "  main.article { overflow: visible; }",
                "  main.article > .content { overflow: visible; }",
                "  article.doc { height: auto; overflow: visible; padding-right: 0; }",
                "  .site-footer { grid-template-columns: 1fr; }",
                "  .site-footer p { justify-self: start; }",
                "}",
                "",
            ]
        ),
    )
    return supplemental_ui


def write_playbook(
    work_root: Path, output_dir: Path, site_url: str, sources: list[Path]
) -> Path:
    supplemental_ui = write_supplemental_ui(work_root)
    source_lines = []
    for source in sources:
        source_lines.extend([f"    - url: {source.as_posix()}", "      branches: HEAD"])

    playbook = work_root / "antora-playbook.yml"
    write_text(
        playbook,
        "\n".join(
            [
                "site:",
                "  title: Beman Docs",
                f"  url: {site_url.rstrip('/')}",
                "  start_page: beman:ROOT:index.adoc",
                "",
                "content:",
                "  sources:",
                *source_lines,
                "",
                "antora:",
                "  extensions:",
                "    - '@antora/collector-extension'",
                "",
                "ui:",
                "  bundle:",
                "    url: https://gitlab.com/antora/antora-ui-default/-/jobs/artifacts/HEAD/raw/build/ui-bundle.zip?job=bundle-stable",
                "    snapshot: true",
                f"  supplemental_files: {supplemental_ui.as_posix()}",
                "",
                "output:",
                f"  dir: {output_dir.as_posix()}",
                "",
            ]
        ),
    )
    return playbook


def build_antora(playbook: Path, cache_dir: Path) -> None:
    run_command(
        [
            "npx",
            "antora",
            "generate",
            str(playbook),
            "--clean",
            "--stacktrace",
            "--cache-dir",
            str(cache_dir),
        ],
        cwd=WEBSITE_ROOT,
        check=True,
    )


def main() -> None:
    args = parse_args()
    check_tools(args.skip_api_reference)

    work_root = args.work_root.resolve()
    output_dir = args.output_dir.resolve()
    shutil.rmtree(work_root, ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)
    work_root.mkdir(parents=True, exist_ok=True)
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    libraries = build_library_docs(
        load_manifest(),
        args.repos_root.resolve(),
        clone_missing=args.clone_missing,
        update_repos=args.update_repos,
    )
    global_nav = write_global_nav(libraries, args.skip_api_reference)

    sources = [write_project_component(work_root, global_nav)]
    for library in libraries:
        sources.append(
            write_library_component(
                work_root,
                library,
                global_nav,
                skip_api_reference=args.skip_api_reference,
            )
        )

    playbook = write_playbook(work_root, output_dir, args.site_url, sources)
    build_antora(playbook, args.cache_dir.resolve())
    print(f"Built unified Antora docs: {output_dir}")


if __name__ == "__main__":
    main()
