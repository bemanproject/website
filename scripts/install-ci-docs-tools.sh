#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

set -euo pipefail

PANDOC_VERSION="3.11"
PANDOC_SHA256="37edb3bbcf722f921a009941bf5874e2e0c09263226c9b4a2d980788cb062ab6"
MRDOCS_VERSION="0.8.0"
MRDOCS_SHA256="75aead343ad5bf6f008efa439a09998fe175718876a05a951d6d6c60e79e671d"

system_name="$(uname -s)"
machine_arch="$(uname -m)"
if [[ ${system_name} != "Linux" || ${machine_arch} != "x86_64" ]]; then
	echo "The CI docs tool installer currently supports Linux x86_64 only." >&2
	exit 1
fi

install_root="${1:-${TMPDIR:-/tmp}/beman-docs-tools}"
downloads_dir="${install_root}/downloads"
bin_dir="${install_root}/bin"
mkdir -p "${downloads_dir}" "${bin_dir}"

download_verified() {
	local url="$1"
	local expected_sha256="$2"
	local destination="$3"

	if [[ -f ${destination} ]]; then
		local cached_sha256
		cached_sha256="$(sha256sum "${destination}" | awk '{print $1}')"
		if [[ ${cached_sha256} == "${expected_sha256}" ]]; then
			return
		fi
	fi

	local temporary="${destination}.tmp"
	curl --fail --location --retry 3 --output "${temporary}" "${url}"
	local actual_sha256
	actual_sha256="$(sha256sum "${temporary}" | awk '{print $1}')"
	if [[ ${actual_sha256} != "${expected_sha256}" ]]; then
		echo "Checksum mismatch for ${url}" >&2
		exit 1
	fi
	mv "${temporary}" "${destination}"
}

pandoc_archive="${downloads_dir}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz"
pandoc_root="${install_root}/pandoc-${PANDOC_VERSION}"
download_verified \
	"https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-linux-amd64.tar.gz" \
	"${PANDOC_SHA256}" \
	"${pandoc_archive}"
if [[ ! -x "${pandoc_root}/bin/pandoc" ]]; then
	mkdir -p "${pandoc_root}"
	tar -xzf "${pandoc_archive}" --strip-components=1 -C "${pandoc_root}"
fi

mrdocs_archive="${downloads_dir}/MrDocs-${MRDOCS_VERSION}-Linux.tar.gz"
mrdocs_root="${install_root}/MrDocs-${MRDOCS_VERSION}-Linux"
download_verified \
	"https://github.com/cppalliance/mrdocs/releases/download/v${MRDOCS_VERSION}/MrDocs-${MRDOCS_VERSION}-Linux.tar.gz" \
	"${MRDOCS_SHA256}" \
	"${mrdocs_archive}"
if [[ ! -x "${mrdocs_root}/bin/mrdocs" ]]; then
	tar -xzf "${mrdocs_archive}" -C "${install_root}"
fi

ln -sfn "../pandoc-${PANDOC_VERSION}/bin/pandoc" "${bin_dir}/pandoc"
ln -sfn "../MrDocs-${MRDOCS_VERSION}-Linux/bin/mrdocs" "${bin_dir}/mrdocs"

"${bin_dir}/pandoc" --version >/dev/null
"${bin_dir}/mrdocs" --version >/dev/null
printf '%s\n' "${bin_dir}"
