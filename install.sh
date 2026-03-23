#!/usr/bin/env bash
# install.sh — Install quant-skills to AI agent skill directories via symlinks.
# Usage: bash install.sh
# Re-run anytime skills are added/renamed to refresh symlinks.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

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

install_skill() {
  local skill_name="$1"
  local target_path="$2"
  local source_path="$REPO_ROOT/skills/$skill_name"

  if [ ! -e "$source_path" ]; then
    echo -e "${YELLOW}[WARN] Skipping $skill_name -- source not found: $source_path${NC}"
    return
  fi

  mkdir -p "$(dirname "$target_path")"

  # Remove existing symlink or warn if real directory
  if [ -L "$target_path" ]; then
    rm "$target_path"
  elif [ -e "$target_path" ]; then
    echo -e "${YELLOW}[WARN] $target_path exists and is not a symlink -- skipping to avoid overwrite${NC}"
    return
  fi

  ln -s "$source_path" "$target_path"
  echo -e "${GREEN}[OK] $skill_name${NC}"
}

echo "Dynamically installing quant-skills..."
echo ""

# Find all subdirectories under skills/ that contain a SKILL.md file
# E.g., skills/finlab/SKILL.md -> finlab
# E.g., skills/nutrlink/data-product-explorer/SKILL.md -> nutrlink/data-product-explorer
SKILLS=()
while IFS= read -r skill_file; do
  # Remove leading "skills/" and trailing "/SKILL.md"
  skill_dir="${skill_file#skills/}"
  skill_dir="${skill_dir%/SKILL.md}"
  SKILLS+=("$skill_dir")
done < <(cd "$REPO_ROOT" && find skills -mindepth 1 -name "SKILL.md" -type f | sort)

if [ ${#SKILLS[@]} -eq 0 ]; then
  echo -e "${YELLOW}[WARN] No skills found (no SKILL.md files located in skills/ directory).${NC}"
  exit 0
fi

# Determine which tools to install
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
  echo -e "${BLUE}-- $tool --${NC}"
  echo "Target: $target_base"

  for skill in "${SKILLS[@]}"; do
    target_path="$target_base/$skill"
    install_skill "$skill" "$target_path"
  done
  echo ""
done

echo "Done. All symlinks installed."
echo ""
echo "To verify Gemini CLI for instance: ls -la ~/.gemini/skills/"
