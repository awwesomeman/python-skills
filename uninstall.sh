#!/usr/bin/env bash
# uninstall.sh — Remove all symlinks created by install.sh.
# Does NOT delete source files in this repository.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Define target directories for all supported AI tools (MacOS Bash v3 compatible arrays)
AI_TOOLS_NAMES=(
  "Antigravity"
  "Claude Code"
  "Codex"
  "Cursor"
  "Gemini CLI"
  "GitHub Copilot"
  "OpenCode"
  "Windsurf"
)

AI_TOOLS_BASES=(
  "$HOME/.gemini/antigravity"
  "$HOME/.claude"
  "$HOME/.agents"
  "$HOME/.cursor"
  "$HOME/.gemini"
  "$HOME/.copilot"
  "$HOME/.config/opencode"
  "$HOME/.codeium/windsurf"
)

AI_TOOLS_PATHS=(
  "$HOME/.gemini/antigravity/skills"
  "$HOME/.claude/skills"
  "$HOME/.agents/skills"
  "$HOME/.cursor/skills"
  "$HOME/.gemini/skills"
  "$HOME/.copilot/skills"
  "$HOME/.config/opencode/skills"
  "$HOME/.codeium/windsurf/skills"
)

AI_TOOLS_ARGS=(
  "antigravity"
  "claude"
  "codex"
  "cursor"
  "gemini"
  "copilot"
  "opencode"
  "windsurf"
)

remove_symlink() {
  local path="$1"
  if [ -L "$path" ]; then
    rm "$path"
    echo -e "${GREEN}Removed: $path${NC}"
  elif [ -e "$path" ]; then
    echo -e "${RED}Not a symlink, skipping: $path${NC}"
  fi
}

echo "Dynamically uninstalling quant-skills symlinks..."
echo ""

# Find all subdirectories under skills/ that contain a SKILL.md file
SKILLS=()
while IFS= read -r skill_file; do
  skill_dir="${skill_file#skills/}"
  skill_dir="${skill_dir%/SKILL.md}"
  SKILLS+=("$skill_dir")
done < <(cd "$REPO_ROOT" && find skills -mindepth 1 -name "SKILL.md" -type f | sort)

if [ ${#SKILLS[@]} -eq 0 ]; then
  echo -e "${YELLOW}[WARN] No skills found in skills/ directory.${NC}"
  exit 0
fi

# Determine which tools to uninstall from
TARGET_INDICES=()

if [ "$#" -eq 0 ]; then
  # Auto-detect mode
  echo "No explicit targets provided. Auto-detecting installed AI tools..."
  for i in "${!AI_TOOLS_NAMES[@]}"; do
    if [ -d "${AI_TOOLS_BASES[$i]}" ]; then
      TARGET_INDICES+=("$i")
      echo -e "${GREEN}Found: ${AI_TOOLS_NAMES[$i]}${NC} (${AI_TOOLS_BASES[$i]})"
    fi
  done
else
  # Manual target mode
  echo "Using specified targets..."
  for arg in "$@"; do
    arg_lower=$(echo "$arg" | tr '[:upper:]' '[:lower:]')
    found=false
    for i in "${!AI_TOOLS_ARGS[@]}"; do
      if [ "${AI_TOOLS_ARGS[$i]}" = "$arg_lower" ]; then
        TARGET_INDICES+=("$i")
        found=true
        echo -e "${GREEN}Selected: ${AI_TOOLS_NAMES[$i]}${NC}"
        break
      fi
    done
    if [ "$found" = false ]; then
      echo -e "${YELLOW}[WARN] Unknown target: $arg (Available: ${AI_TOOLS_ARGS[*]})${NC}"
    fi
  done
fi

echo ""

if [ ${#TARGET_INDICES[@]} -eq 0 ]; then
  echo -e "${YELLOW}[ERROR] No valid AI tools found or specified. Exiting.${NC}"
  echo "Available targets to specify manually: ${AI_TOOLS_ARGS[*]}"
  exit 1
fi

for i in "${TARGET_INDICES[@]}"; do
  tool="${AI_TOOLS_NAMES[$i]}"
  target_base="${AI_TOOLS_PATHS[$i]}"
  echo -e "${BLUE}-- Removing from $tool --${NC}"

  for skill in "${SKILLS[@]}"; do
    target_path="$target_base/$skill"
    remove_symlink "$target_path"
  done
  echo ""
done

echo "Done. Source files in this repository are untouched."
