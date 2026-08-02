#!/usr/bin/env bash
# Install the aur_safety_api (self-updating) version.
#
# Installs alongside the classic aur_safety script as `aur_safety_api`,
# sharing the same config/list directory (~/.config/aur_safety) without
# overwriting the existing aur_safety binary.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.config/aur_safety"
BIN_DIR="${HOME}/.local/bin"

echo "Installing aur_safety_api..."

mkdir -p "${CONFIG_DIR}"
mkdir -p "${BIN_DIR}"

echo "  Copying package lists + manifest to ${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/package_list.txt"       "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/chaos_rat_packages.txt" "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/malicious_npm_packages.txt"      "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/malicious_russian_spam_packages.txt" "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/malicious_elf_dropper_packages.txt" "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/lists.json" "${CONFIG_DIR}/"

echo "  Installing aur_safety_api to ${BIN_DIR}/"
cp "${SCRIPT_DIR}/aur_safety_api" "${BIN_DIR}/aur_safety_api"
chmod +x "${BIN_DIR}/aur_safety_api"

echo ""
echo "Done. Make sure ${BIN_DIR} is in your PATH, then run:"
echo "  aur_safety_api --help"
echo ""
echo "The classic aur_safety script is left untouched. Remove it any time with:"
echo "  rm ${BIN_DIR}/aur_safety"
