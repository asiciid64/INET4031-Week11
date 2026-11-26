# Architecture

The kickoff keeps analysis on the VM host from the Python virtual environment. The existing statustracker app, database, and Prometheus remain the course environment. Week 11 adds a repeatable data generation and evidence path beside that environment.

```mermaid
flowchart LR
  VM[Ubuntu VM] --> VENV[Python venv]
  VENV --> GEN[generate_data.py]
  GEN --> DATA[generated_incidents.csv]
  GEN --> DQ[data_quality.csv]
  VENV --> EVID[collect_evidence.py]
  EVID --> CHECKS[checks.csv]
  EVID --> INDEX[evidence-index.md]
  VM --> K3S[k3s cluster]
  K3S --> WEB[web service]
  K3S --> DB[db pod]
  K3S --> PROM[Prometheus]
  VM --> CHECKPOINT[environment_checkpoint.sh]
  CHECKPOINT --> SNAP[environment-checkpoint.txt]
```

Week 12 will use the generated dataset to produce analysis CSV files, charts, and a statistical check. Week 13 will turn those outputs into the report for Dana.
