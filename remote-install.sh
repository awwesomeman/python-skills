#!/usr/bin/env bash
# remote-install.sh — Download and install python-skills without cloning.
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/awwesomeman/python-skills/main/remote-install.sh | bash
#   curl -fsSL <url> | bash -s -- --skills "python,git" cursor
#   curl -fsSL <url> | bash -s -- --local --skills "python" claude
#
# Environment variables:
#   GITHUB_REPO            Override the default repo (default: awwesomeman/python-skills)
#   PYTHON_SKILLS_BRANCH   Override the branch to download (default: main)
set -euo pipefail

for cmd in curl tar; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "[ERROR] '$cmd' is required but not found." >&2; exit 1; }
done

GITHUB_REPO="${GITHUB_REPO:-awwesomeman/python-skills}"
BRANCH="${PYTHON_SKILLS_BRANCH:-main}"
TARBALL_URL="https://github.com/$GITHUB_REPO/archive/$BRANCH.tar.gz"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

echo -e "${BLUE}Downloading python-skills from $GITHUB_REPO ($BRANCH)...${NC}"
curl -fsSL "$TARBALL_URL" | tar -xz -C "$WORK_DIR"

# GitHub tarball extracts to <repo-name>-<branch>/
EXTRACTED_DIR="$(find "$WORK_DIR" -mindepth 1 -maxdepth 1 -type d | head -1)"

if [ -z "$EXTRACTED_DIR" ] || [ ! -f "$EXTRACTED_DIR/install.sh" ]; then
  echo -e "${YELLOW}[ERROR] install.sh not found in downloaded archive.${NC}"
  exit 1
fi

echo -e "${BLUE}Installing with --copy mode...${NC}"
echo ""
bash "$EXTRACTED_DIR/install.sh" --copy "$@"

echo -e "${GREEN}Remote install complete. Temporary files cleaned up.${NC}"
