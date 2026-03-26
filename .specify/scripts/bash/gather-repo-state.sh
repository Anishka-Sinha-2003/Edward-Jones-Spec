#!/usr/bin/env bash
# gather-repo-state.sh — Collect all repo state into JSON for reporting
#
# Scans specs/ directories, parses frontmatter, checks git state, and
# aggregates into a single JSON document. All report commands call this,
# then format differently.
#
# Usage:
#   bash .specify/scripts/bash/gather-repo-state.sh --json
#
# Output: JSON object with project-level and per-spec state

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

REPO_ROOT=$(get_repo_root)
SPECS_DIR="$REPO_ROOT/specs"
HAS_GIT=$(has_git && echo "true" || echo "false")
HAS_GH=false
if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
  HAS_GH=true
fi

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%Y-%m-%dT%H:%M:%SZ")
STALE_DAYS=14

# --- Helpers ---

# Check if a branch exists (local or remote)
branch_exists() {
  local spec_id="$1"
  if [[ "$HAS_GIT" != "true" ]]; then echo "false"; return; fi
  local pattern="${spec_id}-"
  if git branch -a 2>/dev/null | grep -q "$pattern"; then
    echo "true"
  else
    echo "false"
  fi
}

# Get branch name for a spec directory
get_branch_for_spec() {
  local dirname="$1"
  if [[ "$HAS_GIT" != "true" ]]; then echo ""; return; fi
  local pattern="$dirname"
  git branch -a 2>/dev/null | sed 's/^[* ]*//' | sed 's|remotes/origin/||' | grep -m1 "^${pattern}$" || echo ""
}

# Get last commit date for a path
last_commit_date() {
  local path="$1"
  if [[ "$HAS_GIT" != "true" ]]; then echo ""; return; fi
  git log -1 --format="%Y-%m-%d" -- "$path" 2>/dev/null || echo ""
}

# Get last commit author for a path
last_commit_author() {
  local path="$1"
  if [[ "$HAS_GIT" != "true" ]]; then echo ""; return; fi
  git log -1 --format="%an" -- "$path" 2>/dev/null || echo ""
}

# Get contributors in last N days for a path
recent_contributors() {
  local path="$1" days="${2:-7}"
  if [[ "$HAS_GIT" != "true" ]]; then echo "[]"; return; fi
  local since
  since=$(date -d "-${days} days" +"%Y-%m-%d" 2>/dev/null || date -v-${days}d +"%Y-%m-%d" 2>/dev/null || echo "")
  if [[ -z "$since" ]]; then echo "[]"; return; fi
  local authors
  authors=$(git log --since="$since" --format="%an" -- "$path" 2>/dev/null | sort -u | head -20)
  local result="["
  local first=true
  while IFS= read -r author; do
    [[ -z "$author" ]] && continue
    if $first; then first=false; else result+=","; fi
    result+="\"$(json_escape "$author")\""
  done <<< "$authors"
  result+="]"
  echo "$result"
}

# Calculate days since a date
days_since() {
  local date_str="$1"
  [[ -z "$date_str" ]] && echo "" && return
  local then_ts now_ts
  then_ts=$(date -d "$date_str" +%s 2>/dev/null || date -jf "%Y-%m-%d" "$date_str" +%s 2>/dev/null || echo "")
  now_ts=$(date +%s)
  if [[ -n "$then_ts" ]]; then
    echo $(( (now_ts - then_ts) / 86400 ))
  else
    echo ""
  fi
}

# Check artifact existence and return inventory JSON
get_artifact_inventory() {
  local dir="$1"
  local spec_md="false" design_md="false" tasks_md="false" research_md="false"
  local data_model="false" quickstart="false" contracts="false" checklists="false"

  [[ -f "$dir/spec.md" ]] && spec_md="true"
  [[ -f "$dir/design.md" ]] && design_md="true"
  [[ -f "$dir/tasks.md" ]] && tasks_md="true"
  [[ -f "$dir/research.md" ]] && research_md="true"
  [[ -f "$dir/data-model.md" ]] && data_model="true"
  [[ -f "$dir/quickstart.md" ]] && quickstart="true"
  [[ -d "$dir/contracts" ]] && contracts="true"
  [[ -d "$dir/checklists" ]] && checklists="true"

  echo "{\"spec_md\":$spec_md,\"design_md\":$design_md,\"tasks_md\":$tasks_md,\"research_md\":$research_md,\"data_model\":$data_model,\"quickstart\":$quickstart,\"contracts\":$contracts,\"checklists\":$checklists}"
}

# Derive pipeline status from git/file state
derive_pipeline_status() {
  local dir="$1" spec_id="$2" fm_status="$3"

  # Blocked takes priority
  if [[ "$fm_status" == "blocked" ]]; then echo "blocked"; return; fi

  local has_spec=false has_design=false has_tasks=false
  [[ -f "$dir/spec.md" ]] && has_spec=true
  [[ -f "$dir/design.md" ]] && has_design=true
  [[ -f "$dir/tasks.md" ]] && has_tasks=true

  if $has_tasks; then
    local task_json
    task_json=$(count_tasks "$dir/tasks.md")
    local total done
    total=$(echo "$task_json" | sed 's/.*"total":\([0-9]*\).*/\1/')
    done=$(echo "$task_json" | sed 's/.*"done":\([0-9]*\).*/\1/')

    if [[ "$total" -gt 0 && "$done" -ge "$total" ]]; then
      echo "complete"; return
    elif [[ "$done" -gt 0 ]]; then
      echo "in-dev"; return
    else
      echo "ready"; return
    fi
  fi

  if $has_design; then echo "planning"; return; fi
  if $has_spec; then echo "defining"; return; fi
  echo "drafted"
}

# Get open PR for a branch (graceful degradation)
get_pr_status() {
  local branch="$1"
  if [[ "$HAS_GH" != "true" || -z "$branch" ]]; then echo "{}"; return; fi
  local pr_json
  pr_json=$(gh pr list --head "$branch" --json number,state,title,url --limit 1 2>/dev/null || echo "[]")
  if [[ "$pr_json" == "[]" || -z "$pr_json" ]]; then
    echo "{}"
  else
    echo "$pr_json" | sed 's/^\[//;s/\]$//'
  fi
}

# --- Main collection ---

spec_entries=""
spec_count=0
first_entry=true

if [[ -d "$SPECS_DIR" ]]; then
  for spec_dir in "$SPECS_DIR"/*/; do
    [[ -d "$spec_dir" ]] || continue
    dirname=$(basename "$spec_dir")

    # Skip hidden directories (.project-plan, .architecture, .presales)
    [[ "$dirname" == .* ]] && continue

    spec_id=$(get_spec_id_from_dir "$dirname")
    [[ -z "$spec_id" ]] && continue

    spec_count=$((spec_count + 1))

    # Frontmatter fields
    local_spec="$spec_dir/spec.md"
    fm_title=""
    fm_status="draft"
    fm_owner=""
    fm_parent=""
    fm_priority=""
    fm_effort=""
    fm_deps="[]"
    fm_phase="1"
    fm_tags="[]"
    fm_source=""

    if [[ -f "$local_spec" ]]; then
      fm_title=$(get_frontmatter_field "$local_spec" "title")
      fm_status_raw=$(get_frontmatter_field "$local_spec" "status")
      [[ -n "$fm_status_raw" ]] && fm_status="$fm_status_raw"
      fm_owner=$(get_frontmatter_field "$local_spec" "owner")
      fm_parent=$(get_frontmatter_field "$local_spec" "parent")
      fm_priority=$(get_frontmatter_field "$local_spec" "priority")
      fm_effort=$(get_frontmatter_field "$local_spec" "effort")
      fm_phase=$(get_frontmatter_field "$local_spec" "phase")
      fm_source=$(get_frontmatter_field "$local_spec" "source-authority")
    fi

    # Derived status
    derived_status=$(derive_pipeline_status "$spec_dir" "$spec_id" "$fm_status")

    # Artifact inventory
    artifacts=$(get_artifact_inventory "$spec_dir")

    # Task completion
    task_stats='{"total":0,"done":0,"remaining":0}'
    if [[ -f "$spec_dir/tasks.md" ]]; then
      task_stats=$(count_tasks "$spec_dir/tasks.md")
    fi

    # Activity
    last_date=$(last_commit_date "$spec_dir")
    last_author=$(last_commit_author "$spec_dir")
    contributors=$(recent_contributors "$spec_dir" 7)
    staleness=""
    if [[ -n "$last_date" ]]; then
      days=$(days_since "$last_date")
      if [[ -n "$days" && "$days" -ge "$STALE_DAYS" && "$derived_status" != "complete" ]]; then
        staleness="$days"
      fi
    fi

    # Branch & PR
    branch_name=$(get_branch_for_spec "$dirname")
    has_branch=$(branch_exists "$spec_id")
    pr_info="{}"
    if [[ -n "$branch_name" ]]; then
      pr_info=$(get_pr_status "$branch_name")
    fi

    # Sub-spec detection
    is_sub="false"
    parent_id=""
    if is_sub_spec "$spec_id"; then
      is_sub="true"
      parent_id=$(get_parent_id "$spec_id")
    fi

    # Sub-specs of this spec
    sub_specs="[]"
    if [[ "$is_sub" == "false" ]]; then
      local subs="["
      local sfirst=true
      for sub_dir in "$SPECS_DIR"/${spec_id}.*/; do
        [[ -d "$sub_dir" ]] || continue
        local sub_name
        sub_name=$(basename "$sub_dir")
        local sub_id
        sub_id=$(get_spec_id_from_dir "$sub_name")
        [[ -z "$sub_id" ]] && continue
        if $sfirst; then sfirst=false; else subs+=","; fi
        subs+="\"$sub_id\""
      done
      subs+="]"
      sub_specs="$subs"
    fi

    # Warnings
    warnings="["
    wfirst=true
    # Stale warning
    if [[ -n "$staleness" ]]; then
      wfirst=false
      warnings+="\"stale: no commits in ${staleness} days\""
    fi
    # Unassigned warning
    if [[ -z "$fm_owner" && "$derived_status" != "complete" && "$derived_status" != "drafted" ]]; then
      if $wfirst; then wfirst=false; else warnings+=","; fi
      warnings+="\"unassigned: no owner set\""
    fi
    warnings+="]"

    # Build JSON entry
    if $first_entry; then first_entry=false; else spec_entries+=","; fi
    spec_entries+="{"
    spec_entries+="\"id\":\"$(json_escape "$spec_id")\","
    spec_entries+="\"title\":\"$(json_escape "$fm_title")\","
    spec_entries+="\"directory\":\"$(json_escape "$dirname")\","
    spec_entries+="\"branch\":\"$(json_escape "$branch_name")\","
    spec_entries+="\"has_branch\":$has_branch,"
    spec_entries+="\"frontmatter\":{\"status\":\"$(json_escape "$fm_status")\",\"owner\":\"$(json_escape "$fm_owner")\",\"parent\":\"$(json_escape "$fm_parent")\",\"priority\":\"$(json_escape "$fm_priority")\",\"effort\":\"$(json_escape "$fm_effort")\",\"phase\":$fm_phase,\"source_authority\":\"$(json_escape "$fm_source")\"},"
    spec_entries+="\"derived_status\":\"$(json_escape "$derived_status")\","
    spec_entries+="\"artifacts\":$artifacts,"
    spec_entries+="\"tasks\":$task_stats,"
    spec_entries+="\"activity\":{\"last_commit_date\":\"$(json_escape "$last_date")\",\"last_commit_author\":\"$(json_escape "$last_author")\",\"recent_contributors\":$contributors},"
    spec_entries+="\"staleness_days\":${staleness:-null},"
    spec_entries+="\"pr\":$pr_info,"
    spec_entries+="\"is_sub_spec\":$is_sub,"
    spec_entries+="\"parent_id\":\"$(json_escape "$parent_id")\","
    spec_entries+="\"sub_specs\":$sub_specs,"
    spec_entries+="\"warnings\":$warnings"
    spec_entries+="}"
  done
fi

# Project-level info
has_project_plan="false"
has_architecture="false"
has_presales="false"
has_constitution="false"

[[ -d "$SPECS_DIR/.project-plan" ]] && has_project_plan="true"
[[ -d "$SPECS_DIR/.architecture" ]] && has_architecture="true"
[[ -d "$SPECS_DIR/.presales" ]] && has_presales="true"
[[ -f "$REPO_ROOT/specs/constitution.md" ]] && has_constitution="true"

# Current branch
current_branch="main"
if [[ "$HAS_GIT" == "true" ]]; then
  current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
fi

# Aggregate stats
total_tasks=0
done_tasks=0
if [[ -d "$SPECS_DIR" ]]; then
  for spec_dir in "$SPECS_DIR"/*/; do
    [[ -d "$spec_dir" ]] || continue
    dirname=$(basename "$spec_dir")
    [[ "$dirname" == .* ]] && continue
    if [[ -f "$spec_dir/tasks.md" ]]; then
      local_stats=$(count_tasks "$spec_dir/tasks.md")
      t=$(echo "$local_stats" | sed 's/.*"total":\([0-9]*\).*/\1/')
      d=$(echo "$local_stats" | sed 's/.*"done":\([0-9]*\).*/\1/')
      total_tasks=$((total_tasks + t))
      done_tasks=$((done_tasks + d))
    fi
  done
fi

# Output
cat <<EOJSON
{
  "generated_at": "$NOW",
  "repo_root": "$(json_escape "$REPO_ROOT")",
  "current_branch": "$(json_escape "$current_branch")",
  "has_git": $HAS_GIT,
  "has_gh_cli": $HAS_GH,
  "project": {
    "has_project_plan": $has_project_plan,
    "has_architecture": $has_architecture,
    "has_presales": $has_presales,
    "has_constitution": $has_constitution
  },
  "summary": {
    "spec_count": $spec_count,
    "total_tasks": $total_tasks,
    "done_tasks": $done_tasks,
    "progress_pct": $(if [[ $total_tasks -gt 0 ]]; then echo "$(( (done_tasks * 100) / total_tasks ))"; else echo "0"; fi)
  },
  "specs": [$spec_entries]
}
EOJSON
