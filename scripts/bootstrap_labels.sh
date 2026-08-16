#!/usr/bin/env bash
# Sync the label taxonomy from .github/labels.yml into a GitHub repo.
# Idempotent: `gh label create --force` creates or updates; safe to re-run,
# including to roll taxonomy updates across existing repos.
#
# Usage: scripts/bootstrap_labels.sh [-R owner/repo]
#   -R defaults to the repo of the current directory's origin remote.
# Requires: gh (authenticated), python3 with PyYAML.
set -euo pipefail

REPO_FLAG=()
while getopts "R:" opt; do
  case "$opt" in
    R) REPO_FLAG=(-R "$OPTARG") ;;
    *) echo "usage: $0 [-R owner/repo]" >&2; exit 2 ;;
  esac
done

MANIFEST="$(dirname "$0")/../.github/labels.yml"
[ -f "$MANIFEST" ] || { echo "manifest not found: $MANIFEST" >&2; exit 1; }

python3 - "$MANIFEST" <<'PY' |
import sys, yaml
for row in yaml.safe_load(open(sys.argv[1])):
    print("\t".join([row["name"], row["color"], row.get("description") or ""]))
PY
while IFS=$'\t' read -r name color desc; do
  echo "label: $name"
  gh label create "$name" --color "$color" --description "$desc" --force "${REPO_FLAG[@]}"
done

echo "labels synced from $MANIFEST"
