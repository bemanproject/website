#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import argparse
import os
import re
import shutil
import subprocess  # nosec B404
import sys
import tempfile
from pathlib import Path

import yaml


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "build", "serve"])
    parser.add_argument(
        "--repos-root",
        help="path to folder containing external repos (default: parent of website repo)",
        type=str,
        default="",
    )
    parser.add_argument(
        "--clone-missing",
        help="clone missing repositories listed in beman_libraries_to_import.yaml",
        action="store_true",
    )
    parser.add_argument(
        "--update-repos",
        help="update already checked out repositories to their configured branch tip",
        action="store_true",
    )
    parser.add_argument(
        "--skip-builds",
        help="skip running external repo build commands and only sync existing docs outputs",
        action="store_true",
    )
    parser.add_argument(
        "--work-root",
        help="persistent temporary workspace root (default: system temp dir)",
        type=str,
        default="",
    )
    parser.add_argument(
        "--pages-root",
        help="path to the static output directory (default: repo_root/build)",
        type=str,
        default="",
    )
    parser.add_argument(
        "--skip-api-reference",
        help="skip the Antora/MrDocs API reference build",
        action="store_true",
    )
    return parser.parse_args()


def run_command(*args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(*args, **kwargs)  # nosec B603 B607


def list_tracked_files(repo_root: Path, *paths: str) -> list[Path]:
    result = run_command(
        [
            "git",
            "-C",
            str(repo_root),
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            *paths,
        ],
        check=True,
        capture_output=True,
    )
    entries = [entry for entry in result.stdout.decode().split("\0") if entry]
    return [repo_root / entry for entry in entries]


def copy_tracked_tree(repo_root: Path, stage_root: Path):
    for source in list_tracked_files(repo_root, "."):
        relative_path = source.relative_to(repo_root)
        target = stage_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def stage_repo_content(repo_root: Path, stage_root: Path):
    copy_tracked_tree(repo_root, stage_root)

    for directory in [stage_root / "site_content" / "docs" / "Libraries"]:
        directory.mkdir(parents=True, exist_ok=True)


def strip_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---\n"):
        return {}, content
    end = content.find("\n---\n", 4)
    if end == -1:
        return {}, content
    metadata = yaml.safe_load(content[4:end]) or {}
    body = content[end + len("\n---\n") :]
    return metadata, body.lstrip("\n")


def write_markdown_page(target: Path, metadata: dict, body: str):
    target.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = yaml.safe_dump(metadata, sort_keys=False).strip()
    target.write_text(f"---\n{frontmatter}\n---\n\n{body}")


def copy_tree_if_exists(source: Path, target: Path):
    if source.exists():
        shutil.copytree(source, target, dirs_exist_ok=True)


def copy_static_assets(stage_root: Path, content_root: Path):
    copy_tree_if_exists(stage_root / "static", content_root)
    copy_tree_if_exists(stage_root / "images", content_root / "images")


def migrate_pages(stage_root: Path, content_root: Path):
    shutil.copy2(stage_root / "pages" / "index.md", content_root / "index.md")
    shutil.copy2(stage_root / "pages" / "talks.md", content_root / "talks.md")

    libraries_source = stage_root / "src" / "pages" / "libraries.md"
    metadata, body = strip_frontmatter(libraries_source.read_text())
    metadata["title"] = metadata.get("title", "Beman Libraries")
    body = re.sub(
        r'href="/docs/Libraries/([^"/]+)/"',
        r'href="docs/beman.\1/latest/index.html"',
        body,
    )
    body = re.sub(
        r"\]\(/docs/Libraries/([^/)]+)/\)",
        r"](docs/beman.\1/latest/index.html)",
        body,
    )
    body = body.replace('src="/img/book.svg"', 'src="../img/book.svg"')
    write_markdown_page(content_root / "libraries.md", metadata, body)


def youtube_embed(url: str) -> str:
    video_id = ""
    if "youtu.be/" in url:
        video_id = url.rsplit("/", 1)[-1].split("?", 1)[0]
    elif "youtube.com" in url:
        marker = "v="
        if marker in url:
            video_id = url.split(marker, 1)[1].split("&", 1)[0]
    if not video_id:
        return url
    return (
        '<div class="video-frame">\n'
        f'  <iframe src="https://www.youtube.com/embed/{video_id}" allowfullscreen title="YouTube video"></iframe>\n'
        "</div>"
    )


def first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Blog post"


def normalize_blog_post(source: Path, target: Path, authors: dict) -> dict:
    metadata, body = strip_frontmatter(source.read_text())
    slug = metadata.get("slug") or source.parent.name
    post_date = source.parent.name[:10]
    author_keys = metadata.get("authors") or []
    if isinstance(author_keys, str):
        author_keys = [author_keys]
    author_names = [
        authors.get(author_key, {}).get("name", str(author_key))
        for author_key in author_keys
    ]

    body = "\n".join(
        (
            youtube_embed(line.strip())
            if "youtu.be/" in line or "youtube.com/watch" in line
            else line
        )
        for line in body.splitlines()
    )
    body = body.replace("<!-- truncate -->", "")

    page_meta = {
        "title": first_heading(body),
        "blog_post": True,
        "post_date": post_date,
        "author_names": ", ".join(author_names),
        "comments": bool(metadata.get("comments", False)),
    }
    write_markdown_page(target / "index.md", page_meta, body)
    copy_tree_if_exists(source.parent / "images", target / "images")
    return {
        "title": page_meta["title"],
        "url": f"{slug}/",
        "date": post_date,
        "authors": page_meta["author_names"],
        "tags": metadata.get("tags") or [],
    }


def migrate_blog(stage_root: Path, content_root: Path):
    blog_source = stage_root / "blog"
    blog_target = content_root / "blog"
    blog_target.mkdir(parents=True, exist_ok=True)
    authors = yaml.safe_load((blog_source / "authors.yml").read_text()) or {}
    posts = []

    for source in sorted(blog_source.glob("*/index.md"), reverse=True):
        metadata, _ = strip_frontmatter(source.read_text())
        slug = metadata.get("slug") or source.parent.name
        posts.append(normalize_blog_post(source, blog_target / slug, authors))

    cards = [
        "---",
        "title: Blog",
        "---",
        "",
        "# Blog",
        "",
        '<div class="blog-index">',
    ]
    for post in posts:
        tags = post["tags"]
        if isinstance(tags, str):
            tags = [tags]
        tag_html = "".join(f'<span class="badge">{tag}</span>' for tag in tags)
        cards.extend(
            [
                '<article class="blog-index-item">',
                f'  <time>{post["date"]}</time>',
                "  <div>",
                f'    <h2><a href="{post["url"]}">{post["title"]}</a></h2>',
                (
                    f'    <p class="blog-card-meta">{post["authors"]}</p>'
                    if post["authors"]
                    else ""
                ),
                f'    <div class="blog-tags">{tag_html}</div>' if tag_html else "",
                "  </div>",
                "</article>",
            ]
        )
    cards.append("</div>")
    (blog_target / "index.md").write_text(
        "\n".join(line for line in cards if line) + "\n"
    )


def prepare_mkdocs_content(stage_root: Path):
    content_root = stage_root / "site_content"
    if content_root.exists():
        shutil.rmtree(content_root)
    content_root.mkdir(parents=True)
    copy_static_assets(stage_root, content_root)
    migrate_pages(stage_root, content_root)
    migrate_blog(stage_root, content_root)
    (content_root / "docs").mkdir(parents=True, exist_ok=True)
    (content_root / "docs" / "index.md").write_text("# Docs\n")
    stage_antora_doc_placeholders(stage_root, content_root)


def stage_antora_doc_placeholders(stage_root: Path, content_root: Path):
    manifest_path = stage_root / "beman_libraries_to_import.yaml"
    if not manifest_path.exists():
        return
    manifest = yaml.safe_load(manifest_path.read_text()) or {}
    for repo_name in manifest:
        placeholder = (
            content_root / "docs" / f"beman.{repo_name}" / "latest" / "index.html"
        )
        placeholder.parent.mkdir(parents=True, exist_ok=True)
        placeholder.write_text("")


def build_antora_docs(repo_root: Path, build_root: Path, stage_root: Path, args):
    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "build-antora-docs.py"),
        "--output-dir",
        str(build_root / "docs"),
        "--work-root",
        str(stage_root / "_antora-docs-work"),
        "--cache-dir",
        str(stage_root.parent / "antora-cache"),
        "--site-url",
        os.environ.get("BEMAN_SITE_URL", "http://localhost:8000").rstrip("/") + "/docs",
    ]
    if args.repos_root:
        cmd.extend(["--repos-root", args.repos_root])
    if args.clone_missing:
        cmd.append("--clone-missing")
    if args.update_repos:
        cmd.append("--update-repos")
    if args.skip_api_reference:
        cmd.append("--skip-api-reference")
    run_command(cmd, cwd=repo_root, check=True)


def git_worktree_list(repo_root: Path) -> list[dict[str, str]]:
    output = run_command(
        ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    worktrees = []
    entry: dict[str, str] = {}
    for line in output.splitlines():
        if not line:
            if entry:
                worktrees.append(entry)
                entry = {}
            continue
        key, _, value = line.partition(" ")
        entry[key] = value
    if entry:
        worktrees.append(entry)
    return worktrees


def find_branch_worktree(
    repo_root: Path, branch: str, target_worktree: Path
) -> Path | None:
    branch_ref = f"refs/heads/{branch}"
    target_resolved = target_worktree.resolve()

    for worktree in git_worktree_list(repo_root):
        worktree_path = Path(worktree["worktree"]).resolve()
        if worktree.get("branch") == branch_ref and worktree_path != target_resolved:
            return worktree_path
    return None


def remove_worktree_if_present(repo_root: Path, worktree_path: Path):
    worktree_resolved = worktree_path.resolve()
    for worktree in git_worktree_list(repo_root):
        if Path(worktree["worktree"]).resolve() == worktree_resolved:
            run_command(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "worktree",
                    "remove",
                    "--force",
                    str(worktree_path),
                ],
                check=True,
            )
            break
    shutil.rmtree(worktree_path, ignore_errors=True)


def is_git_worktree(path: Path) -> bool:
    if not path.exists():
        return False
    return (
        run_command(
            ["git", "-C", str(path), "rev-parse", "--git-dir"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def current_worktree_branch(path: Path) -> str:
    return run_command(
        ["git", "-C", str(path), "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def is_dirty_worktree(path: Path) -> bool:
    return bool(
        run_command(
            ["git", "-C", str(path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )


def confirm_replacing_legacy_pages_root(path: Path):
    message = (
        f"Warning: {path} exists and is not a git worktree.\n"
        "It looks like a legacy local build output directory.\n"
        "Delete it and replace it with a gh-pages worktree? [y/N]: "
    )
    if not os.isatty(0):
        raise SystemExit(
            f"{path} exists and is not a git worktree. "
            "Rerun interactively to approve deletion, remove it manually, "
            "or use --pages-root to target a different path."
        )
    response = input(message).strip().lower()
    if response not in {"y", "yes"}:
        raise SystemExit("Aborted before replacing legacy build directory.")


def confirm_moving_branch_worktree(branch: str, source: Path, target: Path):
    dirty_note = ""
    if is_dirty_worktree(source):
        dirty_note = (
            "\nThe existing worktree has uncommitted changes that will be discarded."
        )
    message = (
        f"Branch '{branch}' is already checked out in worktree: {source}\n"
        f"Move that worktree to {target}?{dirty_note} [y/N]: "
    )
    if not os.isatty(0):
        raise SystemExit(
            f"Branch '{branch}' is already checked out in worktree: {source}. "
            f"Rerun interactively to approve moving it to {target}, or remove it manually."
        )
    response = input(message).strip().lower()
    if response not in {"y", "yes"}:
        raise SystemExit(
            f"Aborted before moving '{branch}' worktree from {source} to {target}."
        )


def confirm_replacing_wrong_branch_worktree(
    path: Path, current_branch: str, branch: str
):
    dirty_note = ""
    if is_dirty_worktree(path):
        dirty_note = (
            "\nThe existing worktree has uncommitted changes that will be discarded."
        )
    message = (
        f"Worktree {path} is on branch '{current_branch}', expected '{branch}'.\n"
        f"Replace it with a '{branch}' worktree?{dirty_note} [y/N]: "
    )
    if not os.isatty(0):
        raise SystemExit(
            f"Worktree {path} is on branch '{current_branch}', expected '{branch}'. "
            "Rerun interactively to approve replacing it, remove it manually, "
            "or use --pages-root to target a different path."
        )
    response = input(message).strip().lower()
    if response not in {"y", "yes"}:
        raise SystemExit(
            f"Aborted before replacing '{current_branch}' worktree at {path}."
        )


def ensure_pages_worktree(repo_root: Path, pages_root: Path, branch: str):
    if pages_root.exists() and not is_git_worktree(pages_root):
        confirm_replacing_legacy_pages_root(pages_root)
        shutil.rmtree(pages_root, ignore_errors=True)

    existing_worktree = pages_root.exists() and is_git_worktree(pages_root)
    if existing_worktree:
        current_branch = current_worktree_branch(pages_root)
        if current_branch != branch:
            if os.environ.get("PAGES_DEPLOY") != "true":
                confirm_replacing_wrong_branch_worktree(
                    pages_root, current_branch, branch
                )
            remove_worktree_if_present(repo_root, pages_root)
            existing_worktree = False

    existing_branch_worktree = find_branch_worktree(repo_root, branch, pages_root)
    if existing_branch_worktree:
        confirm_moving_branch_worktree(branch, existing_branch_worktree, pages_root)
        remove_worktree_if_present(repo_root, existing_branch_worktree)

    remote_ref = f"refs/remotes/origin/{branch}"
    local_ref = f"refs/heads/{branch}"
    local_exists_before_fetch = (
        run_command(
            ["git", "-C", str(repo_root), "show-ref", "--verify", "--quiet", local_ref]
        ).returncode
        == 0
    )

    fetch_result = run_command(
        ["git", "-C", str(repo_root), "fetch", "origin", branch],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    fetch_failed = fetch_result.returncode != 0

    remote_exists = (
        run_command(
            ["git", "-C", str(repo_root), "show-ref", "--verify", "--quiet", remote_ref]
        ).returncode
        == 0
    )
    local_exists = (
        run_command(
            ["git", "-C", str(repo_root), "show-ref", "--verify", "--quiet", local_ref]
        ).returncode
        == 0
    )

    if fetch_failed and not (
        existing_worktree or local_exists_before_fetch or local_exists
    ):
        raise SystemExit(
            f"Failed to fetch origin/{branch} and no local '{branch}' branch/worktree is available."
        )

    if not existing_worktree:
        remove_worktree_if_present(repo_root, pages_root)

        if remote_exists:
            if local_exists:
                run_command(
                    [
                        "git",
                        "-C",
                        str(repo_root),
                        "branch",
                        "-f",
                        branch,
                        f"origin/{branch}",
                    ],
                    check=True,
                )
            else:
                run_command(
                    [
                        "git",
                        "-C",
                        str(repo_root),
                        "branch",
                        "--track",
                        branch,
                        f"origin/{branch}",
                    ],
                    check=True,
                )
            run_command(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "worktree",
                    "add",
                    "--force",
                    str(pages_root),
                    branch,
                ],
                check=True,
            )
            run_command(
                ["git", "-C", str(pages_root), "reset", "--hard", f"origin/{branch}"],
                check=True,
            )
        elif local_exists:
            run_command(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "worktree",
                    "add",
                    "--force",
                    str(pages_root),
                    branch,
                ],
                check=True,
            )
            run_command(
                ["git", "-C", str(pages_root), "reset", "--hard", branch],
                check=True,
            )
        else:
            run_command(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "worktree",
                    "add",
                    "--detach",
                    str(pages_root),
                ],
                check=True,
            )
            run_command(
                ["git", "-C", str(pages_root), "checkout", "--orphan", branch],
                check=True,
            )
            run_command(
                ["git", "-C", str(pages_root), "rm", "-rf", "."],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    elif fetch_failed:
        print(
            f"Warning: failed to fetch origin/{branch}; reusing local worktree state."
        )


def prepare_stage_workspace(stage_root: Path, build_root: Path):
    shutil.rmtree(stage_root, ignore_errors=True)
    shutil.rmtree(build_root, ignore_errors=True)
    stage_root.parent.mkdir(parents=True, exist_ok=True)


def sync_build_output(build_root: Path, pages_root: Path, preserve_cname: bool = False):
    rsync_command = [
        "rsync",
        "-a",
        "--delete",
        "--exclude=.git",
    ]
    if preserve_cname and (pages_root / "CNAME").is_file():
        rsync_command.append("--exclude=/CNAME")
    rsync_command.extend([f"{build_root}/", f"{pages_root}/"])
    run_command(
        rsync_command,
        check=True,
    )
    (pages_root / ".nojekyll").touch()
    shutil.rmtree(build_root, ignore_errors=True)


def run_mkdocs(repo_root: Path, stage_root: Path, out_dir: Path, command: str):
    env = os.environ.copy()
    env["BEMAN_WEBSITE_BRANCH"] = (
        run_command(
            ["git", "-C", str(repo_root), "branch", "--show-current"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        or "main"
    )

    if command == "start":
        cmd = [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", "127.0.0.1:8000"]
    elif command == "build":
        cmd = [sys.executable, "-m", "mkdocs", "build", "--site-dir", str(out_dir)]
    else:
        cmd = [sys.executable, "-m", "http.server", "8000", "--directory", str(out_dir)]

    run_command(cmd, cwd=stage_root, check=True, env=env)


def fix_mkdocs_output_links(build_root: Path):
    libraries_page = build_root / "libraries" / "index.html"
    if not libraries_page.exists():
        return
    content = libraries_page.read_text()
    content = content.replace('href="docs/beman.', 'href="../docs/beman.')
    libraries_page.write_text(content)


def build_composed_site(repo_root: Path, build_root: Path, stage_root: Path, args):
    run_mkdocs(repo_root, stage_root, build_root, "build")
    fix_mkdocs_output_links(build_root)
    build_antora_docs(repo_root, build_root, stage_root, args)


def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    default_work_root = Path(tempfile.gettempdir()) / "beman-website-work"
    work_root = Path(args.work_root) if args.work_root else default_work_root
    if os.environ.get("CI") == "true":
        args.clone_missing = True
        args.update_repos = True
        if not args.repos_root:
            args.repos_root = str(work_root / "external-repos")
    pages_root = Path(args.pages_root) if args.pages_root else repo_root / "build"
    stage_root = work_root / "site"
    build_root = work_root / "_build"

    prepare_stage_workspace(stage_root, build_root)
    stage_repo_content(repo_root, stage_root)
    prepare_mkdocs_content(stage_root)

    if args.command == "start":
        build_composed_site(repo_root, build_root, stage_root, args)
        run_mkdocs(repo_root, stage_root, build_root, "serve")
        return

    publishing_to_gh_pages = (
        not args.pages_root and os.environ.get("PAGES_DEPLOY") == "true"
    )
    if publishing_to_gh_pages:
        ensure_pages_worktree(repo_root, pages_root, "gh-pages")
    else:
        pages_root.mkdir(parents=True, exist_ok=True)

    build_composed_site(repo_root, build_root, stage_root, args)
    sync_build_output(
        build_root,
        pages_root,
        preserve_cname=publishing_to_gh_pages,
    )

    if args.command == "serve":
        run_mkdocs(repo_root, stage_root, pages_root, "serve")
    else:
        print(f"Built site output: {pages_root}")


if __name__ == "__main__":
    main()
