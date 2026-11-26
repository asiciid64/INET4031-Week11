#!/usr/bin/env python3
"""Collect repeatable Week 11 kickoff evidence.

Run from the repository root with the data science virtual environment.
The script writes evidence/checks.csv and evidence/evidence-index.md.
"""

from __future__ import annotations

import csv
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = BASE / "evidence"

SECRET_PATTERNS = [
    re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(password|api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]+['\"]"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(command, cwd=REPO, text=True, capture_output=True, timeout=20, check=False)
        return result.returncode, (result.stdout + result.stderr).strip()
    except Exception as exc:
        return 1, f"{type(exc).__name__}: {exc}"


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, str]] = []

    def add(name: str, status: str, detail: str, evidence: str) -> None:
        checks.append({"check": name, "status": status, "detail": detail, "evidence": evidence})

    required_files = [
        "README.md",
        "capstone/data-science/DATA.md",
        "capstone/data-science/control-matrix.md",
        "capstone/data-science/control-matrix.csv",
        "capstone/data-science/risk-register.md",
        "capstone/data-science/risk-register.csv",
        "capstone/data-science/scripts/generate_data.py",
        "capstone/data-science/scripts/collect_evidence.py",
        "capstone/data-science/scripts/environment_checkpoint.sh",
        "capstone/data-science/data/generated_incidents.csv",
        "capstone/data-science/output/data_quality.csv",
        "capstone/data-science/TOOL-VERSIONS.txt",
        "capstone/data-science/requirements.txt",
        "docs/qa-report-final.md",
    ]
    for relative in required_files:
        path = REPO / relative
        add(f"file exists {relative}", "PASS" if path.exists() else "FAIL", "present" if path.exists() else "missing", relative)

    code, branch = run(["git", "branch", "--show-current"])
    add("kickoff branch", "PASS" if branch == "week11-kickoff" else "FAIL", branch or "no branch output", "git branch --show-current")

    data_path = BASE / "data/generated_incidents.csv"
    if data_path.exists():
        frame = pd.read_csv(data_path, parse_dates=["created_at", "resolved_at"])
        span_days = int((frame["created_at"].max() - frame["created_at"].min()).days + 1)
        closed = frame["status"].eq("closed")
        add("dataset row count", "PASS" if len(frame) >= 10000 else "FAIL", f"{len(frame)} rows", "data/generated_incidents.csv")
        add("dataset date coverage", "PASS" if span_days >= 90 else "FAIL", f"{span_days} days", "data/generated_incidents.csv")
        add("category completeness", "PASS" if frame["category"].notna().all() and frame["category"].ne("").all() else "FAIL", f"{int(frame['category'].isna().sum())} null categories", "output/data_quality.csv")
        add("closed resolution completeness", "PASS" if frame.loc[closed, "resolved_at"].notna().all() else "FAIL", f"{int(frame.loc[closed, 'resolved_at'].isna().sum())} closed rows missing resolved_at", "output/data_quality.csv")
        add("synthetic marker", "PASS" if frame["synthetic"].astype(str).str.lower().isin(["true", "1"]).all() else "FAIL", "all rows marked synthetic", "data/generated_incidents.csv")

    quality_path = BASE / "output/data_quality.csv"
    if quality_path.exists():
        quality = pd.read_csv(quality_path)
        add("data quality gates", "PASS" if quality["status"].eq("PASS").all() else "FAIL", f"{int(quality['status'].eq('PASS').sum())} of {len(quality)} checks pass", "output/data_quality.csv")

    control_path = BASE / "control-matrix.csv"
    if control_path.exists():
        controls = pd.read_csv(control_path)
        add("control matrix count", "PASS" if len(controls) >= 15 else "FAIL", f"{len(controls)} controls", "control-matrix.csv")

    risk_path = BASE / "risk-register.csv"
    if risk_path.exists():
        risks = pd.read_csv(risk_path)
        reduced = bool((risks["score_after"] < risks["score_before"]).all())
        add("risk register remediation", "PASS" if reduced else "FAIL", f"{len(risks)} risks with after scores below before scores", "risk-register.csv")

    secret_hits = []
    for path in REPO.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".sh", ".txt", ".csv", ".yml", ".yaml"}:
            continue
        if "generated_incidents.csv" in path.name:
            continue
        text = path.read_text(errors="ignore")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            secret_hits.append(str(path.relative_to(REPO)))
    add("secret pattern scan", "PASS" if not secret_hits else "FAIL", "no secret patterns found" if not secret_hits else ", ".join(secret_hits), "repository text files")

    for tool in ["python3", "git", "jq"]:
        add(f"tool available {tool}", "PASS" if shutil.which(tool) else "UNAVAILABLE", shutil.which(tool) or "not found", "environment checkpoint")
    for tool in ["kubectl", "psql", "duckdb", "docker"]:
        add(f"tool available {tool}", "PASS" if shutil.which(tool) else "UNAVAILABLE", shutil.which(tool) or "not found in this environment", "environment checkpoint")

    checks_path = EVIDENCE_DIR / "checks.csv"
    with checks_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["check", "status", "detail", "evidence"])
        writer.writeheader()
        writer.writerows(checks)

    key_files = [REPO / relative for relative in required_files if (REPO / relative).exists()]
    lines = [
        "# Evidence Index",
        "",
        "This file is generated by capstone/data-science/scripts/collect_evidence.py.",
        "",
        "## Check summary",
        "",
        f"Total checks: {len(checks)}",
        f"Pass: {sum(1 for item in checks if item['status'] == 'PASS')}",
        f"Fail: {sum(1 for item in checks if item['status'] == 'FAIL')}",
        f"Unavailable: {sum(1 for item in checks if item['status'] == 'UNAVAILABLE')}",
        "",
        "Unavailable means the tool was not present in the environment where the script ran. Run the environment checkpoint on the Ubuntu k3s VM to capture cluster evidence there.",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail | Evidence |",
        "|---|---|---|---|",
    ]
    for item in checks:
        lines.append(f"| {item['check']} | {item['status']} | {item['detail']} | {item['evidence']} |")
    lines += ["", "## Key file hashes", "", "| File | Bytes | SHA256 |", "|---|---:|---|"]
    for path in key_files:
        lines.append(f"| {path.relative_to(REPO)} | {path.stat().st_size} | {sha256(path)} |")
    (EVIDENCE_DIR / "evidence-index.md").write_text("\n".join(lines) + "\n")

    print(f"Wrote {checks_path}")
    print(f"Wrote {EVIDENCE_DIR / 'evidence-index.md'}")
    return 1 if any(item["status"] == "FAIL" for item in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
