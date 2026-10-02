# Scripts

This directory contains scripts for the Beman Project website.

## sync-docs.py

This script is used to sync the Beman Project documentation from the `beman/` repo to this `website/` repo.

Steps:

1. Copy images from `beman/images/` to `website/images/` and `website/static/images/`.
2. Copy documentation from `beman/docs/` to `website/docs/`.
3. Insert sidebar position into the documentation files.

```shell
$ python3 scripts/sync-docs.py --help
usage: sync-docs.py [-h] beman_repo_path

positional arguments:
  beman_repo_path  path to root of beman repo to clone from

optional arguments:
  -h, --help       show this help message and exit

$ python3 scripts/sync-docs.py ../beman
Copying images from ../beman/images to /Users/dariusn/dev/dn/git/Beman/website/images
Copying images from ../beman/images to /Users/dariusn/dev/dn/git/Beman/website/static/images
Copying ../beman/docs/README.md to /Users/dariusn/dev/dn/git/Beman/website/docs/README.md
Inserting sidebar position 1 into /Users/dariusn/dev/dn/git/Beman/website/docs/README.md
Copying ../beman/docs/beman_library_maturity_model.md to /Users/dariusn/dev/dn/git/Beman/website/docs/beman_library_maturity_model.md
Inserting sidebar position 2 into /Users/dariusn/dev/dn/git/Beman/website/docs/beman_library_maturity_model.md
Copying ../beman/docs/beman_standard.md to /Users/dariusn/dev/dn/git/Beman/website/docs/beman_standard.md
Inserting sidebar position 3 into /Users/dariusn/dev/dn/git/Beman/website/docs/beman_standard.md
Copying ../beman/docs/mission.md to /Users/dariusn/dev/dn/git/Beman/website/docs/mission.md
Inserting sidebar position 4 into /Users/dariusn/dev/dn/git/Beman/website/docs/mission.md
Copying ../beman/docs/faq.md to /Users/dariusn/dev/dn/git/Beman/website/docs/faq.md
Inserting sidebar position 5 into /Users/dariusn/dev/dn/git/Beman/website/docs/faq.md
Copying ../beman/docs/governance.md to /Users/dariusn/dev/dn/git/Beman/website/docs/governance.md
Inserting sidebar position 6 into /Users/dariusn/dev/dn/git/Beman/website/docs/governance.md
Copying ../beman/docs/code_of_conduct.md to /Users/dariusn/dev/dn/git/Beman/website/docs/code_of_conduct.md
Inserting sidebar position 7 into /Users/dariusn/dev/dn/git/Beman/website/docs/code_of_conduct.md
```

## sync-external-docs.py

Sync generated documentation outputs from external repos into a destination root.

Configured repos are listed in `beman_libraries_to_import.yaml`.

```shell
$ python3 scripts/sync-external-docs.py --output-root /tmp/website-stage
Building docs in /path/to/optional with: make docs
Copying /path/to/optional/docs/html to /tmp/website-stage/static/optional

# Override the parent folder containing external repos
$ python3 scripts/sync-external-docs.py --repos-root ../ --output-root /tmp/website-stage

# In CI: clone missing repos and update them before syncing docs
$ python3 scripts/sync-external-docs.py --repos-root /tmp/beman-external --clone-missing --update-repos --output-root /tmp/website-stage
```

## run-staged-website.py

Prepare a temporary staged MkDocs content tree, overlay generated library docs, then run MkDocs against that staged content.

By default this uses a persistent temporary workspace rooted at:

```shell
$TMPDIR/beman-website-work/
```

Its final staged source tree lives at:

```shell
$TMPDIR/beman-website-work/site/
```

Its final rendered artifacts live in the local `build/` directory by default:

```shell
/path/to/website/build/
```

Set `PAGES_DEPLOY=true` to make the default `build/` directory a `gh-pages`
worktree for publishing. Normal local and preview builds do not fetch or require
the `gh-pages` branch. Publishing preserves an existing root `CNAME` file so a
configured GitHub Pages custom domain is not cleared by deployment.

When `CI=true`, configured library repositories are cloned into the temporary
workspace as needed and updated to `main`. Local builds continue to use adjacent
library checkouts unless `--clone-missing` or `--repos-root` is specified.

`install-ci-docs-tools.sh` installs pinned, checksum-verified Pandoc and MrDocs
Linux binaries for CI. GitHub Actions and Netlify use this same installer.

```shell
$ python3 scripts/run-staged-website.py start
$ python3 scripts/run-staged-website.py build
$ python3 scripts/run-staged-website.py serve
```

`make` and `make start` are equivalent and both go through this staged workflow.

## publish-gh-pages.sh

Publish an existing `gh-pages` worktree to the remote `gh-pages` branch.

```shell
$ bash scripts/publish-gh-pages.sh gh-pages
$ bash scripts/publish-gh-pages.sh gh-pages /tmp/custom-gh-pages-worktree
```
