#!/usr/bin/env bash
# generate-commands.sh — Build tool-specific command files from shared prompts
#
# Reads shared prompt bodies from .specify/prompts/ and generates:
#
#   Per-command:
#     .claude/commands/*.md                    Claude Code (YAML frontmatter + body)
#     .github/agents/*.agent.md               GitHub Copilot custom agents (name/description + body)
#     .cursor/skills/{name}/SKILL.md             Cursor Skills (plain markdown)
#
#   Repo-level instructions (from .specify/repo-instructions.md):
#     CLAUDE.md                                Claude Code
#     AGENTS.md                                GitHub Copilot Coding Agent
#     .github/copilot-instructions.md          GitHub Copilot Chat & completions
#     .cursorrules                             Cursor (deprecated, migrate to Skills)
#
# Usage:
#   bash .specify/scripts/bash/generate-commands.sh           # generate all
#   bash .specify/scripts/bash/generate-commands.sh --check   # CI validation
#
# The --check flag compares generated output against committed files and exits
# non-zero if anything is stale. Useful as a pre-commit hook or CI step.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" \
  || REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"

PROMPTS_DIR="$REPO_ROOT/.specify/prompts"
CLAUDE_OUT="$REPO_ROOT/.claude/commands"
COPILOT_OUT="$REPO_ROOT/.github/agents"
CURSOR_OUT="$REPO_ROOT/.cursor/skills"

CHECK_MODE=false
if [[ "${1:-}" == "--check" ]]; then
  CHECK_MODE=true
fi

# Verify prompts directory exists
if [[ ! -d "$PROMPTS_DIR" ]]; then
  echo "ERROR: Prompts directory not found: $PROMPTS_DIR"
  echo "Expected shared prompt files at .specify/prompts/*.md"
  exit 1
fi

# Count prompt files (exclude sidecar yaml files)
prompt_count=0
for f in "$PROMPTS_DIR"/*.md; do
  [[ -f "$f" ]] && prompt_count=$((prompt_count + 1))
done

if [[ $prompt_count -eq 0 ]]; then
  echo "ERROR: No prompt files found in $PROMPTS_DIR"
  exit 1
fi

mkdir -p "$CLAUDE_OUT" "$COPILOT_OUT" "$CURSOR_OUT"

stale=0
generated=0

# Helper: compare tmp file against output, report stale or copy
check_or_generate() {
  local label="$1" tmp_file="$2" out_file="$3"
  if $CHECK_MODE; then
    if [[ ! -f "$out_file" ]]; then
      echo "MISSING: $label"
      stale=1
    elif ! diff -q "$tmp_file" "$out_file" >/dev/null 2>&1; then
      echo "STALE:   $label"
      stale=1
    fi
  else
    mkdir -p "$(dirname "$out_file")"
    cp "$tmp_file" "$out_file"
  fi
}

# --- Generate per-command files ---

for prompt_file in "$PROMPTS_DIR"/*.md; do
  [[ -f "$prompt_file" ]] || continue

  name="$(basename "$prompt_file" .md)"
  claude_yaml="$PROMPTS_DIR/$name.claude.yaml"
  copilot_yaml="$PROMPTS_DIR/$name.copilot.yaml"
  claude_out_file="$CLAUDE_OUT/$name.md"
  copilot_out_file="$COPILOT_OUT/$name.agent.md"
  cursor_out_file="$CURSOR_OUT/$name/SKILL.md"

  # Extract description from claude.yaml (first description: line)
  description=""
  if [[ -f "$claude_yaml" ]]; then
    description="$(grep -m1 '^description:' "$claude_yaml" | sed 's/^description:[[:space:]]*//' | sed 's/^["'"'"']//;s/["'"'"']$//')"
  fi

  # Derive Copilot agent name: dots → hyphens (e.g., ais.spec.specify → ais-spec-specify)
  agent_name="${name//./-}"

  # Build Claude command: YAML frontmatter + prompt body
  build_claude() {
    if [[ -f "$claude_yaml" ]]; then
      echo "---"
      cat "$claude_yaml"
      echo "---"
    fi
    echo ""
    echo "<!-- Generated from .specify/prompts/$name.md — do not edit directly -->"
    echo ""
    cat "$prompt_file"
  }

  # Build Copilot agent: name/description/handoffs frontmatter + prompt body
  build_copilot() {
    echo "---"
    if [[ -f "$copilot_yaml" ]]; then
      cat "$copilot_yaml"
    else
      echo "name: \"$agent_name\""
      if [[ -f "$claude_yaml" ]]; then
        # Reuse description and handoffs from the Claude sidecar.
        # Strip allowed-tools (Claude-specific) and convert agent
        # name dots to hyphens in handoff entries.
        sed -e '/^allowed-tools:/d' \
            -e '/^    agent: /s/\./-/g' \
            "$claude_yaml"
      else
        echo "description: \"$description\""
      fi
    fi
    echo "---"
    echo ""
    echo "<!-- Generated from .specify/prompts/$name.md — do not edit directly -->"
    echo ""
    cat "$prompt_file"
  }

  # Build Cursor skill: plain markdown (no frontmatter)
  build_cursor() {
    echo "<!-- Generated from .specify/prompts/$name.md — do not edit directly -->"
    echo ""
    cat "$prompt_file"
  }

  tmp_claude=$(mktemp)
  tmp_copilot=$(mktemp)
  tmp_cursor=$(mktemp)

  build_claude > "$tmp_claude"
  build_copilot > "$tmp_copilot"
  build_cursor > "$tmp_cursor"

  check_or_generate ".claude/commands/$name.md" "$tmp_claude" "$claude_out_file"
  check_or_generate ".github/agents/$name.agent.md" "$tmp_copilot" "$copilot_out_file"
  check_or_generate ".cursor/skills/$name/SKILL.md" "$tmp_cursor" "$cursor_out_file"

  rm -f "$tmp_claude" "$tmp_copilot" "$tmp_cursor"

  if ! $CHECK_MODE; then
    generated=$((generated + 1))
    echo "  $name"
  fi
done

# --- Generate repo-level instructions from .specify/repo-instructions.md ---

REPO_INSTRUCTIONS="$REPO_ROOT/.specify/repo-instructions.md"
CLAUDE_MD="$REPO_ROOT/CLAUDE.md"
AGENTS_MD="$REPO_ROOT/AGENTS.md"
COPILOT_INSTRUCTIONS="$REPO_ROOT/.github/copilot-instructions.md"
CURSOR_RULES="$REPO_ROOT/.cursorrules"

if [[ -f "$REPO_INSTRUCTIONS" ]]; then
  HTML_HEADER="<!-- Generated from .specify/repo-instructions.md by generate-commands.sh — do not edit directly -->"
  COMMENT_HEADER="# Generated from .specify/repo-instructions.md by generate-commands.sh — do not edit directly"

  build_with_html_header() {
    echo "$HTML_HEADER"
    echo ""
    cat "$REPO_INSTRUCTIONS"
  }

  build_with_comment_header() {
    echo "$COMMENT_HEADER"
    echo ""
    cat "$REPO_INSTRUCTIONS"
  }

  # CLAUDE.md
  tmp=$(mktemp)
  build_with_html_header > "$tmp"
  check_or_generate "CLAUDE.md" "$tmp" "$CLAUDE_MD"
  if ! $CHECK_MODE; then echo "  CLAUDE.md"; fi
  rm -f "$tmp"

  # AGENTS.md (GitHub Copilot Coding Agent)
  tmp=$(mktemp)
  build_with_html_header > "$tmp"
  check_or_generate "AGENTS.md" "$tmp" "$AGENTS_MD"
  if ! $CHECK_MODE; then echo "  AGENTS.md"; fi
  rm -f "$tmp"

  # .github/copilot-instructions.md (Copilot Chat & completions)
  tmp=$(mktemp)
  build_with_html_header > "$tmp"
  check_or_generate ".github/copilot-instructions.md" "$tmp" "$COPILOT_INSTRUCTIONS"
  if ! $CHECK_MODE; then echo "  copilot-instructions.md"; fi
  rm -f "$tmp"

  # .cursorrules (deprecated — kept for backward compat)
  tmp=$(mktemp)
  build_with_comment_header > "$tmp"
  check_or_generate ".cursorrules" "$tmp" "$CURSOR_RULES"
  if ! $CHECK_MODE; then echo "  .cursorrules (deprecated)"; fi
  rm -f "$tmp"

else
  echo "WARNING: .specify/repo-instructions.md not found — skipping repo-level instructions"
fi

# --- Report ---

if $CHECK_MODE; then
  if [[ $stale -eq 1 ]]; then
    echo ""
    echo "Generated command files are out of date."
    echo "Run: bash .specify/scripts/bash/generate-commands.sh"
    exit 1
  else
    echo "All generated command files are up to date."
  fi
else
  echo ""
  echo "Generated $generated command(s) for Claude Code, GitHub Copilot, and Cursor."
  echo "  Claude:  .claude/commands/"
  echo "  Copilot: .github/agents/"
  echo "  Cursor:  .cursor/skills/"

  # Clean up old .cursor/rules/*.mdc files (migrated to Skills)
  if [[ -d "$REPO_ROOT/.cursor/rules" ]]; then
    rm -f "$REPO_ROOT/.cursor/rules"/*.mdc
    rmdir "$REPO_ROOT/.cursor/rules" 2>/dev/null || true
  fi
fi
