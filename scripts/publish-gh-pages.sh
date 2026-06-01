#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="${1:-gh-pages}"
WORKTREE_DIR="${2:-${REPO_ROOT}/build}"
SOURCE_SHA="$(git -C "${REPO_ROOT}" rev-parse --short HEAD)"

if [[ ! -d ${WORKTREE_DIR} ]]; then
	echo "gh-pages worktree not found: ${WORKTREE_DIR}" >&2
	exit 1
fi

if ! git -C "${WORKTREE_DIR}" rev-parse --git-dir >/dev/null 2>&1; then
	echo "Not a git worktree: ${WORKTREE_DIR}" >&2
	exit 1
fi

CURRENT_BRANCH="$(git -C "${WORKTREE_DIR}" rev-parse --abbrev-ref HEAD)"
if [[ ${CURRENT_BRANCH} != "${BRANCH}" ]]; then
	echo "Expected branch '${BRANCH}' in ${WORKTREE_DIR}, found '${CURRENT_BRANCH}'" >&2
	exit 1
fi

git -C "${WORKTREE_DIR}" add -A

if git -C "${WORKTREE_DIR}" diff --cached --quiet; then
	echo "No gh-pages changes to publish."
	exit 0
fi

git -C "${WORKTREE_DIR}" commit -m "Deploy website from ${SOURCE_SHA}"
git -C "${WORKTREE_DIR}" push origin HEAD:"${BRANCH}"
