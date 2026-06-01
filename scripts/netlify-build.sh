#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

set -euo pipefail

cache_root="${NETLIFY_CACHE_DIR:-${TMPDIR:-/tmp}}"
tool_bin="$(bash scripts/install-ci-docs-tools.sh "${cache_root}/beman-docs-tools")"
export PATH="${tool_bin}:${PATH}"

if [[ -n ${DEPLOY_PRIME_URL-} ]]; then
	export BEMAN_SITE_URL="${DEPLOY_PRIME_URL}"
fi

npm run build
