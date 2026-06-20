#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HOME}/.config/aur_safety"
BIN_DIR="${HOME}/.local/bin"

echo "Installing aur_safety..."

mkdir -p "${CONFIG_DIR}"
mkdir -p "${BIN_DIR}"

echo "  Copying package lists to ${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/package_list.txt"       "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/chaos_rat_packages.txt" "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/malicious_npm_packages.txt"      "${CONFIG_DIR}/"
cp "${SCRIPT_DIR}/malicious_russian_spam_packages.txt" "${CONFIG_DIR}/"

echo "  Installing aur_safety to ${BIN_DIR}/"
cp "${SCRIPT_DIR}/aur_safety" "${BIN_DIR}/aur_safety"
chmod +x "${BIN_DIR}/aur_safety"

echo ""
echo "Done. Make sure ${BIN_DIR} is in your PATH, then run:"
echo "  aur_safety --help"
