#!/usr/bin/env bash
# _config.sh — Shared AI Tools configuration for install.sh and uninstall.sh.
# Source this file; do not execute directly.

AI_TOOLS_NAMES=(
  "Antigravity"
  "Claude Code"
  "Codex"
  "Cursor"
  "Gemini CLI"
  "GitHub Copilot"
  "OpenCode"
  "Windsurf"
  "OpenClaw"
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
  "$HOME/.openclaw"
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
  "$HOME/.openclaw/skills"
)

AI_TOOLS_LOCAL_PATHS=(
  ".agent/skills"
  ".claude/skills"
  ".agents/skills"
  ".cursor/skills"
  ".gemini/skills"
  ".github/skills"
  ".opencode/skills"
  ".windsurf/skills"
  ".openclaw/skills"
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
  "openclaw"
)
