#!/usr/bin/env bash

set -u
set -o pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "=== RiskOps Copilot: Running full pipeline ==="

run_step() {
  local label="$1"
  shift

  echo
  echo ">>> ${label}"
  echo "+ $*"

  "$@"
  local status=$?
  if [ "${status}" -ne 0 ]; then
    echo "ERROR: step failed: ${label}" >&2
    echo "ERROR: command failed: $*" >&2
    exit 1
  fi
}

run_step "Generate synthetic data" python scripts/generate_synthetic_data.py
run_step "Build warehouse" python scripts/build_warehouse.py
run_step "Detect anomalies" python scripts/detect_anomalies.py
run_step "Run attribution" python scripts/run_attribution.py
run_step "Render M3 summary" python scripts/render_m3_report.py
run_step "Render model lab outputs" python scripts/riskops_cli.py render-model-lab

run_step "M3 summary CLI" python scripts/riskops_cli.py summary
run_step "Anomalies CLI" python scripts/riskops_cli.py anomalies
run_step "Drivers CLI" python scripts/riskops_cli.py drivers
run_step "Model lab CLI" python scripts/riskops_cli.py model-lab
run_step "ML baseline CLI" python scripts/riskops_cli.py ml-baseline
run_step "ML readiness CLI" python scripts/riskops_cli.py ml-readiness
run_step "Briefing CLI" python scripts/riskops_cli.py briefing
run_step "Render dashboard CLI" python scripts/riskops_cli.py render-dashboard
run_step "Render report CLI" python scripts/riskops_cli.py render-report
run_step "Render Excel report" python scripts/riskops_cli.py render-excel
run_step "Render Plotly charts" python scripts/riskops_cli.py render-charts
run_step "QC scan demo" python scripts/riskops_cli.py qc-scan --texts "你赶快还钱" "我是法院，马上起诉你" "请尽快联系我们安排还款"
run_step "Script generation demo" python scripts/riskops_cli.py script --case-id CASE00000001 --channel sms
# C2 DONE

echo
echo "=== RiskOps Copilot: Output files ==="
find outputs/ -type f
