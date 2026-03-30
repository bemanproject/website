#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import argparse
import shutil
from pathlib import Path


def parse_args():
    """
    Parse the CLI arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "beman_repo_path", help="path to root of beman repo to clone from", type=str
    )
    args = parser.parse_args()

    return args


def copy_images(beman_repo_path: Path, website_repo_path: Path):
    """
    Copy directory beman/images/ to /static/images/ for website build.
    Copy directory beman/images/ to / for previews in editors.
    """
    tasks = [
        {
            "source": beman_repo_path / "images",
            "target": website_repo_path / "images",
        },
        {
            "source": beman_repo_path / "images",
            "target": website_repo_path / "static" / "images",
        },
        {
            "source": beman_repo_path / "docs" / "images",
            "target": website_repo_path / "docs" / "images",
        },
        {
            "source": beman_repo_path / "docs" / "images",
            "target": website_repo_path / "static" / "docs" / "images",
        },
    ]

    for task in tasks:
        beman_images_path = task["source"]
        target_directory = task["target"]
        print(f"Copying images from {beman_images_path} to {target_directory}")

        # Remove the target_directory if it exists and create it again.
        if target_directory.exists():
            shutil.rmtree(target_directory)
        shutil.copytree(beman_images_path, target_directory)


def insert_sidebar_metadata(file_path: Path, sidebar_position: int, sidebar_label: str):
    """
    Insert the sidebar position into the file.
    Literally insert 3 (or 4) lines at the top of the file:
        ---
        sidebar_position: {sidebar_position}
        sidebar_label: {sidebar_label}
        ---
    """
    with open(file_path, "r") as file:
        lines = file.readlines()
    prefix = [
        f"---\n",
        f"sidebar_position: {sidebar_position}\n",
    ]
    if sidebar_label:
        prefix.append(f"sidebar_label: {sidebar_label}\n")
    else:
        raise ValueError(f"No side label provided for {file_path}")
    prefix.append(f"---\n")
    prefix.append(f"\n")
    with open(file_path, "w") as file:
        file.writelines(prefix + lines)


def sync_beman_docs(
    beman_repo_path: Path,
    website_repo_path: Path,
    relative_path: str,
    sidebar_position: int,
    sidebar_label: str = "",
):
    """
    Copy beman/{relative_path} to /docs/{relative_path} for website build.
    Insert the sidebar position into the file.
    """
    beman_path = beman_repo_path / relative_path
    website_path = website_repo_path / relative_path
    print(f"Copying {beman_path} to {website_path}")
    shutil.copy(beman_path, website_path)

    print(f"Inserting sidebar position {sidebar_position} into {website_path}")
    insert_sidebar_metadata(website_path, sidebar_position, sidebar_label=sidebar_label)


def main():
    """
    The sync-docs main entry point.
    """
    args = parse_args()

    beman_repo_path = Path(args.beman_repo_path)
    website_repo_path = Path(__file__).parent.parent

    copy_images(beman_repo_path, website_repo_path)
    sync_beman_docs(
        beman_repo_path,
        website_repo_path,
        "docs/README.md",
        1,
        sidebar_label="Docs",
    )
    sync_beman_docs(
        beman_repo_path,
        website_repo_path,
        "docs/beman_library_maturity_model.md",
        2,
        sidebar_label="Beman Library Maturity Model",
    )
    sync_beman_docs(
        beman_repo_path,
        website_repo_path,
        "docs/beman_standard.md",
        3,
        sidebar_label="Beman Standard",
    )
    sync_beman_docs(
        beman_repo_path,
        website_repo_path,
        "docs/mission.md",
        4,
        sidebar_label="Mission",
    )
    sync_beman_docs(
        beman_repo_path, website_repo_path, "docs/faq.md", 5, sidebar_label="FAQ"
    )
    sync_beman_docs(
        beman_repo_path,
        website_repo_path,
        "docs/governance.md",
        6,
        sidebar_label="Governance",
    )
    sync_beman_docs(
        beman_repo_path,
        website_repo_path,
        "docs/code_of_conduct.md",
        7,
        sidebar_label="Code of Conduct",
    )


if __name__ == "__main__":
    main()
