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
  echo "Tickets table check (Local VM track checkpoint):"
  SQL_SH=""
  for candidate in "$REPO_ROOT/week-10/sql.sh" "$HOME/week-10/sql.sh" "$(dirname "$REPO_ROOT")/week-10/sql.sh"; do
    if [ -x "$candidate" ]; then
      SQL_SH="$candidate"
      break
    fi
  done
  if [ -n "$SQL_SH" ]; then
    echo "Using $SQL_SH"
    "$SQL_SH" "SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM tickets" 2>&1
  elif command -v kubectl >/dev/null 2>&1 && kubectl get deploy/db >/dev/null 2>&1; then
    echo "week-10/sql.sh not found next to this repo; querying the db pod directly."
    kubectl exec -i deploy/db -- sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM tickets;"' 2>&1
  else
    echo "tickets check unavailable here. On the VM run: ./week-10/sql.sh \"SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM tickets\""
  fi
  echo ""
  echo "Prometheus check (Local VM track checkpoint):"
  PROM_URL="${PROM_URL:-http://localhost:9090}"
  if curl -s --max-time 3 "$PROM_URL/-/healthy" >/dev/null 2>&1; then
    echo "Prometheus healthy at $PROM_URL"
    curl -s --max-time 5 "$PROM_URL/api/v1/query" --data-urlencode 'query=up' 2>&1 | head -c 2000
    echo ""
  else
    echo "Prometheus not reachable at $PROM_URL. Start the port-forward in its own terminal and leave it in the foreground:"
    echo "kubectl port-forward --namespace monitoring service/prometheus-server 9090:80"
    echo "Then run ./week-6/pq.sh 'up' from the course repo, or rerun this script."
  fi
  echo ""
  echo "Local health check:"
  curl -s --max-time 3 http://localhost:8080/health 2>&1 || echo "localhost:8080 health check unavailable in this environment"
} > "$OUT"

echo "Wrote $OUT"

# Regenerate the Task 5 tool-version evidence from this machine, so a VM run
# replaces the sandbox-generated copies with the versions actually used.
TOOL_OUT="$REPO_ROOT/capstone/data-science/TOOL-VERSIONS.txt"
{
  echo "Tool versions used for Week 11 kickoff"
  echo "Generated UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Hostname: $(hostname)"
  echo "Python: $(python3 --version 2>&1)"
  if [ -x "$HOME/data-science-venv/bin/python" ]; then
    "$HOME/data-science-venv/bin/python" - <<'PY'
import matplotlib
import pandas
import scipy
print(f"pandas: {pandas.__version__}")
print(f"matplotlib: {matplotlib.__version__}")
print(f"scipy: {scipy.__version__}")
PY
    echo "csvkit: $("$HOME/data-science-venv/bin/csvstat" --version 2>&1)"
  else
    echo "data-science-venv not found at $HOME/data-science-venv"
  fi
  for tool in git jq psql duckdb kubectl; do
    if command -v "$tool" >/dev/null 2>&1; then
      echo "$tool: $("$tool" --version 2>&1 | head -1)"
    else
      echo "$tool: not found in this environment"
    fi
  done
  echo "psql is optional for the Local VM because sql.sh and kubectl exec reach the db pod. DuckDB CLI is a single binary install on Ubuntu."
} > "$TOOL_OUT"

echo "Wrote $TOOL_OUT"

if [ -x "$HOME/data-science-venv/bin/pip" ]; then
  "$HOME/data-science-venv/bin/pip" freeze > "$REPO_ROOT/capstone/data-science/requirements.txt"
  echo "Wrote $REPO_ROOT/capstone/data-science/requirements.txt"
fi
