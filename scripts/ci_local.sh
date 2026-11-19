#!/usr/bin/env bash
# Same checks as .github/workflows/ci.yml, after dependencies are installed.
set -euo pipefail
cd "$(dirname "$0")/.."

if command -v python >/dev/null 2>&1; then
  PY=python
else
  PY=python3
fi

"$PY" -m pytest tests/ -v --tb=short

"$PY" scripts/validate_schemas.py

"$PY" src/triage_agent.py --mock --input examples/sample_request.txt > /tmp/smoke_output.json
"$PY" -c "import json; d=json.load(open('/tmp/smoke_output.json')); assert 'triage_id' in d; print('Smoke test passed')"

"$PY" eval/evaluate.py --output /tmp/eval_report.json
"$PY" -c "
import json
report = json.load(open('/tmp/eval_report.json'))
agreement = report['summary']['agreement_rate']
errors = report['summary']['errors']
print(f'Smoke test agreement: {agreement}%')
if errors > 0:
    print(f'ERROR: {errors} test case(s) failed to process')
    raise SystemExit(1)
print('Evaluation smoke test passed')
"

"$PY" scripts/governance_check.py
"$PY" scripts/build_llms_full.py --check
echo "Local CI checks passed"
