#!/usr/bin/env bash
# install.sh - Idempotent installer for six6.
# Usage: bash install.sh --base-dir <target> [--six6-dir <repo-root>]
set -euo pipefail

BASE_DIR=""
SIX6_DIR="$(cd "$(dirname "$0")/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-dir)  BASE_DIR="$2";  shift 2 ;;
    --six6-dir)  SIX6_DIR="$2";  shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$BASE_DIR" ]]; then
  echo "Error: --base-dir is required." >&2
  exit 1
fi

echo "==> Initializing six6 base dir at: $BASE_DIR"
python3 "$SIX6_DIR/runtime/scripts/six6.py" init --base-dir "$BASE_DIR"

EXAMPLES_DIR="$BASE_DIR/examples"
mkdir -p "$EXAMPLES_DIR"

for tpl in cron.example systemd.example; do
  src="$SIX6_DIR/distribution/templates/$tpl"
  dst="$EXAMPLES_DIR/$tpl"
  if [[ ! -f "$dst" ]]; then
    cp "$src" "$dst"
    echo "    Copied $tpl -> $EXAMPLES_DIR/"
  else
    echo "    Skipped $tpl (already exists)"
  fi
done

echo ""
echo "==> Next steps:"
echo ""
echo "  Validate protocol files:"
echo "    python3 $SIX6_DIR/runtime/scripts/six6.py validate --base-dir $BASE_DIR"
echo ""
echo "  Run health check:"
echo "    python3 $SIX6_DIR/runtime/scripts/six6.py doctor --base-dir $BASE_DIR"
echo ""
echo "  Fire a heartbeat pulse:"
echo "    python3 $SIX6_DIR/runtime/scripts/six6.py pulse heartbeat --base-dir $BASE_DIR"
echo ""
echo "  Review scheduling examples:"
echo "    cat $EXAMPLES_DIR/cron.example"
echo "    cat $EXAMPLES_DIR/systemd.example"
echo ""
echo "==> Installation complete."
