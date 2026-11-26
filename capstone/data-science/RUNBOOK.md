# Runbook

## Purpose

This runbook covers the Week 11 kickoff for the Applied Data Science track. It explains how to set up tools, generate the dataset, collect evidence, and save the environment checkpoint.

## Setup

Create the virtual environment in the home directory.

```bash
python3 -m venv ~/data-science-venv
~/data-science-venv/bin/pip install --upgrade pip
~/data-science-venv/bin/pip install -r capstone/data-science/requirements.txt
```

## Generate data

```bash
~/data-science-venv/bin/python capstone/data-science/scripts/generate_data.py
```

This writes capstone/data-science/data/generated_incidents.csv and capstone/data-science/output/data_quality.csv.

## Collect evidence

```bash
~/data-science-venv/bin/python capstone/data-science/scripts/collect_evidence.py
bash capstone/data-science/scripts/environment_checkpoint.sh
```

This writes capstone/data-science/evidence/checks.csv, capstone/data-science/evidence/evidence-index.md, and capstone/data-science/evidence/environment-checkpoint.txt.

## Cluster checkpoint on the Ubuntu k3s VM

Run the checkpoint script on the VM where kubectl is configured. The script records nodes, pods, and the web health check when the web Service is available.

## Recovery

If the dataset looks wrong, rerun generate_data.py. The fixed seed recreates the same dataset. If evidence files look stale, rerun collect_evidence.py and environment_checkpoint.sh. If the virtual environment is broken, remove it and recreate it from requirements.txt.
