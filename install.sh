#!/usr/bin/env bash
# install.sh — Install skills to AI agent skill directories via symlinks.
# Usage: bash install.sh [--skills "git,python,quant"] [AI_TOOLS...]
# Re-run anytime skills are added/renamed to refresh symlinks.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# shellcheck source=_config.sh
source "$REPO_ROOT/_config.sh"

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

echo "Dynamically installing skills..."
echo ""

# Parse arguments
SELECTED_SKILLS=()
EXPLICIT_TARGETS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -s|--skills)
      if [ -n "${2:-}" ]; then
        IFS=',' read -ra SELECTED_SKILLS <<< "$2"
        shift 2
      else
        echo -e "${YELLOW}[ERROR] --skills requires a comma-separated list of skills${NC}"
        exit 1
      fi
      ;;
    *)
      EXPLICIT_TARGETS+=("$1")
      shift
      ;;
  esac
done

# Find all valid skills
ALL_SKILLS=()
while IFS= read -r skill_file; do
  skill_dir="${skill_file#skills/}"
  skill_dir="${skill_dir%/SKILL.md}"
  ALL_SKILLS+=("$skill_dir")
done < <(cd "$REPO_ROOT" && find skills -mindepth 1 -name "SKILL.md" -type f | sort)

if [ ${#ALL_SKILLS[@]} -eq 0 ]; then
  echo -e "${YELLOW}[WARN] No skills found (no SKILL.md files located in skills/ directory).${NC}"
  exit 0
fi

# Filter skills based on --skills argument
SKILLS=()
if [ ${#SELECTED_SKILLS[@]} -eq 0 ]; then
  SKILLS=("${ALL_SKILLS[@]}")
else
  for found in "${ALL_SKILLS[@]}"; do
    for target in "${SELECTED_SKILLS[@]}"; do
      if [[ "$found" == "$target" || "$found" == "$target/"* ]]; then
        SKILLS+=("$found")
        break
      fi
    done
  done
fi

if [ ${#SKILLS[@]} -eq 0 ]; then
  echo -e "${YELLOW}[WARN] No skills matched the specified --skills filter: ${SELECTED_SKILLS[*]}${NC}"
  exit 0
fi

# Determine target AI tools
TARGET_INDICES=()

if [ ${#EXPLICIT_TARGETS[@]} -eq 0 ]; then
  echo "No explicit targets provided. Auto-detecting installed AI tools..."
  for i in "${!AI_TOOLS_NAMES[@]}"; do
    if [ -d "${AI_TOOLS_BASES[$i]}" ]; then
      TARGET_INDICES+=("$i")
      echo -e "${GREEN}Found: ${AI_TOOLS_NAMES[$i]}${NC} (${AI_TOOLS_BASES[$i]})"
    fi
  done
else
  echo "Using specified targets..."
  for arg in "${EXPLICIT_TARGETS[@]}"; do
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
