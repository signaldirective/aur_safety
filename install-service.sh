#!/usr/bin/env bash
# Install the aur_safety list collector as a systemd user service.
#
# Requirements:
#   - This repo cloned to a local path (the clone becomes WorkingDirectory)
#   - An SSH deploy key at ~/.ssh/aur_safety_deploy with push access to the repo
#     (or edit the generated unit to use your usual SSH auth)
#
# Usage:
#   ./install-service.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$(dirname "${SCRIPT_DIR}")" && pwd)"
UNIT_DIR="${HOME}/.config/systemd/user"

mkdir -p "${UNIT_DIR}"

for unit in aur-safety-lists.service aur-safety-lists.timer; do
    sed -e "s|__REPO_DIR__|${REPO_ROOT}|g" \
        "${SCRIPT_DIR}/systemd/${unit}" > "${UNIT_DIR}/${unit}"
    echo "Installed ${UNIT_DIR}/${unit}"
done

systemctl --user daemon-reload
systemctl --user enable --now aur-safety-lists.timer

echo ""
echo "Installed. Check status with:"
echo "  systemctl --user list-timers aur-safety-lists.timer"
echo "  systemctl --user status aur-safety-lists.service"
echo ""
echo "Note: create an SSH deploy key at ~/.ssh/aur_safety_deploy with push"
echo "access to the aur_safety repo, or adjust GIT_SSH_COMMAND in"
echo "${UNIT_DIR}/aur-safety-lists.service"
