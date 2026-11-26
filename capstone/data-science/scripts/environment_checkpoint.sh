#!/usr/bin/env bash
set +e

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT="$REPO_ROOT/capstone/data-science/evidence/environment-checkpoint.txt"
mkdir -p "$(dirname "$OUT")"

{
  echo "Environment checkpoint"
  echo "Generated UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Hostname: $(hostname)"
  echo "OS: $(uname -a)"
  echo "Repository: $REPO_ROOT"
  echo "Git branch: $(git -C "$REPO_ROOT" branch --show-current 2>/dev/null)"
  echo "Git status:"
  git -C "$REPO_ROOT" status --short 2>/dev/null
  echo ""
  echo "Python:"
  python3 --version 2>&1
  if [ -x "$HOME/data-science-venv/bin/python" ]; then
    "$HOME/data-science-venv/bin/python" - <<'PY'
import matplotlib
import pandas
import scipy
print(f"pandas {pandas.__version__}")
print(f"matplotlib {matplotlib.__version__}")
print(f"scipy {scipy.__version__}")
PY
    "$HOME/data-science-venv/bin/csvstat" --version 2>&1
  else
    echo "data-science-venv not found at $HOME/data-science-venv"
  fi
  echo ""
  echo "System tools:"
  for tool in git jq psql duckdb kubectl docker; do
    if command -v "$tool" >/dev/null 2>&1; then
      echo "$tool: $(command -v "$tool")"
      "$tool" --version 2>&1 | head -1
    else
      echo "$tool: not found in this environment"
    fi
  done
  echo ""
  echo "Cluster checks:"
  if command -v kubectl >/dev/null 2>&1; then
    kubectl get nodes 2>&1
    kubectl get pods -A 2>&1 | head -80
    WEB_IP="$(kubectl get service web -o jsonpath='{.spec.clusterIP}' 2>/dev/null)"
    if [ -n "$WEB_IP" ]; then
      echo "Web health:"
      curl -s --max-time 5 "http://$WEB_IP:8080/health" 2>&1
      echo ""
    fi
  else
    echo "kubectl not found. Run this checkpoint on the Ubuntu k3s VM for cluster evidence."
  fi
  echo ""
  echo "Local health check:"
  curl -s --max-time 3 http://localhost:8080/health 2>&1 || echo "localhost:8080 health check unavailable in this environment"
} > "$OUT"

echo "Wrote $OUT"
