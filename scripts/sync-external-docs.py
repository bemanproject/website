#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

from __future__ import annotations

import argparse
import posixpath
import re
import shutil
import subprocess  # nosec B404
from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).resolve().parent.parent / "beman_libraries_to_import.yaml"
SPECIAL_LABELS = {
    "debug-ci": "Debugging CI",
    "using_exemplar": "Using Exemplar",
    "using_cstring_view": "Guide",
    "design_rationale": "Design Rationale",
}
MARKDOWN_LINK_RE = re.compile(
    r"(?P<prefix>!?\[[^\]]*\]\()(?P<href>[^\s)]+)(?P<suffix>(?:\s+[^)]*)?\))"
)
GITHUB_BLOB_URL_RE = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/blob/(?P<branch>[^/]+)/(?P<path>.+)$"
)


def run_command(*args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(*args, **kwargs)  # nosec B603 B607


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repos-root",
        help="path to folder containing external repos (default: parent of website repo)",
        type=str,
        default="",
    )
    parser.add_argument(
        "--skip-builds",
        help="skip running build commands and only sync existing docs outputs",
        action="store_true",
    )
    parser.add_argument(
        "--clone-missing",
        help="clone missing repositories listed in config",
        action="store_true",
    )
    parser.add_argument(
        "--update-repos",
        help="update already checked out repositories to their configured branch tip",
        action="store_true",
    )
    parser.add_argument(
        "--output-root",
        help="destination root for generated docs (default: website repo root)",
        type=str,
        default="",
    )
    parser.add_argument(
        "--checked-out-only",
        help="restrict sync to repos whose resolved local path already exists",
        action="store_true",
    )
    return parser.parse_args()


def load_repo_manifest() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text()) or {}


def try_resolve_repo_path(
    path_value: str | None, website_repo_path: Path, repos_root: Path, repo_name: str
) -> Path:
    candidates: list[Path] = []
    if path_value:
        path = Path(path_value)
        candidates.extend(
            [path, (website_repo_path / path).resolve(), (Path.cwd() / path).resolve()]
        )
    candidates.append(repos_root / repo_name)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[-1]


def infer_build_config(repo_path: Path, repo_name: str) -> dict:
    makefile = repo_path / "Makefile"
    if not makefile.exists():
        return {}

    contents = makefile.read_text()
    if "docs:" not in contents:
        return {}

    docs_output_rel = Path("docs") / "html"
    return {
        "build_cmd": ["make", "docs"],
        "docs_output_rel": docs_output_rel,
        "static_target_rel": Path(repo_name),
    }


def target_rel_to_permalink(target_rel: Path) -> str:
    parts = target_rel.parts
    if not parts or parts[0] != "docs":
        return f"/{target_rel.as_posix()}"
    doc_parts = (
        parts[:-1]
        if target_rel.name == "index.md"
        else target_rel.with_suffix("").parts
    )
    permalink = "/" + "/".join(doc_parts)
    return permalink + "/" if target_rel.name == "index.md" else permalink


def make_sidebar_label(target_name: str) -> str:
    stem = Path(target_name).stem
    if stem.lower() == "readme":
        return "README"
    if stem in SPECIAL_LABELS:
        return SPECIAL_LABELS[stem]
    return stem.replace("_", " ").replace("-", " ").title()


def parse_file_entry(entry) -> tuple[Path, Path]:
    if isinstance(entry, str):
        source_rel = Path(entry)
        target_rel = (
            Path(*source_rel.parts[1:])
            if source_rel.parts and source_rel.parts[0] == "docs"
            else source_rel
        )
        return source_rel, target_rel
    if isinstance(entry, dict) and len(entry) == 1:
        [(source, target)] = entry.items()
        return Path(source), Path(target)
    raise ValueError(f"Unsupported file entry: {entry!r}")


def generate_repo_docs_from_manifest(
    manifest: dict,
    website_repo_path: Path,
    repos_root: Path,
    checked_out_only: bool = False,
) -> list[dict]:
    repos = []
    for repo_name, raw_config in manifest.items():
        config = raw_config or {}
        if not config.get("files", []):
            print(f"No files configured for {repo_name}, skipping")
            continue
        repo_path = try_resolve_repo_path(
            config.get("path"), website_repo_path, repos_root, repo_name
        )
        if checked_out_only and not repo_path.exists():
            print(f"Repo {repo_name} not checked out at {repo_path}, skipping")
            continue

        repo = {
            "name": repo_name,
            "path": repo_path,
            "repo_url": f"https://github.com/bemanproject/{repo_name}",
            "repo_branch": "main",
            "configured_files": config.get("files", []),
        }

        repos.append(repo)
    return repos


def populate_discovered_repo_metadata(repo: dict, repo_path: Path):
    repo_name = repo["name"]
    repo.update(infer_build_config(repo_path, repo_name))

    markdown_docs = [
        {
            "target_rel": Path("docs") / "Libraries" / repo_name / "index.md",
            "sidebar_position": 1,
            "sidebar_label": f"beman.{repo_name}",
            "generated": "index",
        }
    ]

    next_position = 2
    if (repo_path / "README.md").exists():
        markdown_docs.append(
            {
                "source_rel": Path("README.md"),
                "target_rel": Path("docs") / "Libraries" / repo_name / "readme.md",
                "sidebar_position": next_position,
                "sidebar_label": "README",
                "repo_root_doc": True,
            }
        )
        next_position += 1

    for position, entry in enumerate(
        repo.get("configured_files", []), start=next_position
    ):
        source_rel, target_spec = parse_file_entry(entry)
        target_rel = Path("docs") / "Libraries" / repo_name / target_spec
        markdown_docs.append(
            {
                "source_rel": source_rel,
                "target_rel": target_rel,
                "sidebar_position": position,
                "sidebar_label": make_sidebar_label(target_rel.name),
            }
        )

    repo["markdown_docs"] = markdown_docs
    repo["source_link_map"] = {
        doc["source_rel"].as_posix(): doc["target_rel"].name
        for doc in markdown_docs
        if "source_rel" in doc
    }


def run_build(repo_path: Path, build_cmd: list[str]) -> bool:
    print(f"Building docs in {repo_path} with: {' '.join(build_cmd)}")
    try:
        run_command(build_cmd, cwd=repo_path, check=True)
        return True
    except subprocess.CalledProcessError as exc:
        print(f"Build failed in {repo_path} (exit {exc.returncode})")
        return False


def ensure_repo(repo: dict, clone_missing: bool, update_repos: bool) -> Path:
    repo_path = repo["path"]
    repo_url = repo.get("repo_url", "")
    repo_branch = repo.get("repo_branch", "main")

    if not repo_path.exists() and clone_missing and repo_url:
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Cloning {repo_url} into {repo_path}")
        run_command(
            [
                "git",
                "clone",
                "--branch",
                repo_branch,
                "--single-branch",
                repo_url,
                str(repo_path),
            ],
            check=True,
        )

    if repo_path.exists() and update_repos:
        print(f"Updating {repo_path} to origin/{repo_branch}")
        run_command(["git", "fetch", "origin", repo_branch], cwd=repo_path, check=True)
        run_command(["git", "checkout", repo_branch], cwd=repo_path, check=True)
        run_command(
            ["git", "pull", "--ff-only", "origin", repo_branch],
            cwd=repo_path,
            check=True,
        )

    return repo_path


def copy_docs(source: Path, target: Path) -> bool:
    if not source.exists():
        print(f"Missing docs output: {source}")
        return False
    print(f"Copying {source} to {target}")
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    return True


def copy_markdown_with_frontmatter(
    source: Path,
    target: Path,
    sidebar_position: int,
    sidebar_label: str,
    repo_url: str = "",
    repo_branch: str = "main",
    intro_block: str = "",
    source_link_map: dict[str, str] | None = None,
    source_repo_path: Path | None = None,
    rewrite_repo_relative_links: bool = False,
) -> bool:
    if source and not source.exists():
        print(f"Missing markdown source: {source}")
        return False

    target.parent.mkdir(parents=True, exist_ok=True)
    content = source.read_text() if source else ""
    content = enable_markdown_in_details(content)
    content = rewrite_repo_links(
        content,
        repo_url,
        repo_branch,
        source_link_map=source_link_map,
        source_repo_path=source_repo_path,
        source_rel=(
            source.relative_to(source_repo_path)
            if source and source_repo_path
            else None
        ),
        rewrite_relative_links=rewrite_repo_relative_links,
    )
    if intro_block:
        content = intro_block + "\n\n" + content
        content = content.replace("\n# Overview", "\n## Overview", 1)

    if not content.lstrip().startswith("---"):
        frontmatter = (
            "---\n"
            f"title: {sidebar_label}\n"
            f"sidebar_position: {sidebar_position}\n"
            f"sidebar_label: {sidebar_label}\n"
            "---\n\n"
        )
        content = frontmatter + content

    target.write_text(content)
    print(f"Copied markdown {source} to {target}")
    return True


def enable_markdown_in_details(content: str) -> str:
    return re.sub(
        r"<details(?![^>]*\bmarkdown=)([^>]*)>", r'<details markdown="1"\1>', content
    )


def rewrite_repo_links(
    content: str,
    repo_url: str,
    repo_branch: str,
    source_link_map: dict[str, str] | None = None,
    source_repo_path: Path | None = None,
    source_rel: Path | None = None,
    rewrite_relative_links: bool = False,
) -> str:
    if not repo_url:
        return content

    replacements = {
        "](.github/": f"]({repo_url}/tree/{repo_branch}/.github/",
        "](./.github/": f"]({repo_url}/tree/{repo_branch}/.github/",
        "](../.github/": f"]({repo_url}/tree/{repo_branch}/.github/",
    }
    for old, new in replacements.items():
        content = content.replace(old, new)

    content = rewrite_github_blob_image_links(content)

    if rewrite_relative_links:
        content = rewrite_relative_markdown_links(
            content,
            repo_url,
            repo_branch,
            source_link_map or {},
            source_repo_path,
            source_rel,
        )
    return content


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
        or href.startswith("/")
        or href.startswith("//")
        or bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href))
    )


def normalize_repo_relative_path(path: str) -> str:
    return path.removeprefix("./")


def resolve_repo_relative_path(path: str, repo_path: Path | None) -> str:
    normalized = normalize_repo_relative_path(path)
    if not repo_path:
        return normalized

    if (repo_path / normalized).exists():
        return normalized

    pluralized = normalized + "s"
    if (repo_path / pluralized).exists():
        return pluralized

    return normalized


def github_relative_url(
    repo_url: str,
    repo_branch: str,
    path: str,
    is_image: bool,
    repo_path: Path | None = None,
) -> str:
    path = resolve_repo_relative_path(path, repo_path)
    if is_image:
        return f"{repo_url}/raw/{repo_branch}/{path}"
    kind = "tree" if path.endswith("/") or "." not in Path(path).name else "blob"
    return f"{repo_url}/{kind}/{repo_branch}/{path}"


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


def rewrite_relative_markdown_links(
    content: str,
    repo_url: str,
    repo_branch: str,
    source_link_map: dict[str, str],
    source_repo_path: Path | None,
    source_rel: Path | None,
) -> str:
    source_dir = source_rel.parent.as_posix() if source_rel else ""

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
            (candidate for candidate in candidates if candidate in source_link_map),
            "",
        )
        if synced_path:
            href = source_link_map[synced_path] + suffix
        else:
            repo_path = next(
                (
                    candidate
                    for candidate in candidates
                    if source_repo_path and (source_repo_path / candidate).exists()
                ),
                candidates[-1],
            )
            href = github_relative_url(
                repo_url,
                repo_branch,
                repo_path,
                is_image=match.group("prefix").startswith("!"),
                repo_path=source_repo_path,
            )
            if suffix:
                href += suffix

        return f"{match.group('prefix')}{href}{match.group('suffix')}"

    return rewrite_markdown_links_outside_fences(content, replace)


def build_index_block(repo: dict) -> str:
    repo_name = repo.get("name", "")
    repo_url = repo.get("repo_url", "")
    static_target_rel = repo.get("static_target_rel")
    api_path = (
        f"/{static_target_rel.as_posix()}/index.html" if static_target_rel else ""
    )
    parts = [
        f"# {repo_name}",
        "",
        "Links:",
        "",
    ]
    if repo_url:
        parts.append(f"- [Repository]({repo_url})")
    if api_path:
        parts.append(f'- <a href="{api_path}" data-noBrokenLinkCheck>API reference</a>')
    for doc in repo.get("markdown_docs", []):
        if doc.get("generated") == "index":
            continue
        parts.append(f"- [{doc['sidebar_label']}]({doc['target_rel'].name})")
    return "\n".join(parts)


def main():
    args = parse_args()
    website_repo_path = Path(__file__).parent.parent
    repos_root = Path(args.repos_root) if args.repos_root else website_repo_path.parent
    output_root = Path(args.output_root) if args.output_root else website_repo_path
    manifest = load_repo_manifest()
    repos = generate_repo_docs_from_manifest(
        manifest,
        website_repo_path,
        repos_root,
        checked_out_only=args.checked_out_only,
    )

    failures = 0
    for repo in repos:
        repo_path = ensure_repo(
            repo,
            clone_missing=args.clone_missing,
            update_repos=args.update_repos,
        )
        if not repo_path.exists():
            print(f"Missing repo checkout: {repo_path}")
            failures += 1
            continue

        populate_discovered_repo_metadata(repo, repo_path)

        build_ok = True
        if not args.skip_builds and "build_cmd" in repo:
            build_ok = run_build(repo_path, repo["build_cmd"])
            if not build_ok:
                failures += 1

        if build_ok and "docs_output_rel" in repo and "static_target_rel" in repo:
            source = repo_path / repo["docs_output_rel"]
            target = output_root / repo["static_target_rel"]
            if not copy_docs(source, target):
                failures += 1

        for doc in repo.get("markdown_docs", []):
            md_source = repo_path / doc["source_rel"] if "source_rel" in doc else None
            md_target = output_root / doc["target_rel"]
            intro_block = ""
            if doc.get("generated") == "index":
                intro_block = build_index_block(repo)
            if not copy_markdown_with_frontmatter(
                md_source,
                md_target,
                doc["sidebar_position"],
                doc["sidebar_label"],
                repo_url=repo.get("repo_url", ""),
                repo_branch=repo.get("repo_branch", "main"),
                intro_block=intro_block,
                source_link_map=repo.get("source_link_map", {}),
                source_repo_path=repo_path,
                rewrite_repo_relative_links="source_rel" in doc,
            ):
                failures += 1

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
