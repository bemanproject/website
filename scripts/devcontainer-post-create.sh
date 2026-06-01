#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

set -euo pipefail

tool_bin="$(bash scripts/install-ci-docs-tools.sh "${HOME}/.local/share/beman-docs-tools")"
sudo ln -sfn "${tool_bin}/pandoc" /usr/local/bin/pandoc
sudo ln -sfn "${tool_bin}/mrdocs" /usr/local/bin/mrdocs

make install

trunk_installer="$(mktemp)"
curl --fail --location --output "${trunk_installer}" https://get.trunk.io
chmod +x "${trunk_installer}"
"${trunk_installer}"
rm -f "${trunk_installer}"
