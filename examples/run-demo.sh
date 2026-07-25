#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_DIR="${ROOT_DIR}/examples/rename-demo"

python3 "${DEMO_DIR}/demo_rename.py" \
  --input "${DEMO_DIR}/fixtures/eingang.txt" \
  --output "${DEMO_DIR}/out/ergebnis.md" \
  --rules-dir "${ROOT_DIR}/rules"

python3 "${DEMO_DIR}/check_schema.py" \
  --results "${DEMO_DIR}/out/ergebnis.md" \
  --schema "${ROOT_DIR}/rules/SCHEMA.md"

echo
echo "## Absichtlicher FAIL-Pfad"
if python3 "${DEMO_DIR}/check_schema.py" \
  --name "2026-03-14 Musterlieferant Rechnung.pdf" \
  --schema "${ROOT_DIR}/rules/SCHEMA.md"; then
  echo "FEHLER: Der ungueltige Beispielname wurde akzeptiert." >&2
  exit 1
else
  echo "OK: Der ungueltige Beispielname wurde erwartungsgemaess abgelehnt."
fi
