#!/usr/bin/env python3
"""Generate the Week 11 synthetic Harborlight incident dataset.

The generator uses a fixed seed and writes the dataset plus data_quality.csv.
It plants the patterns documented in DATA.md so the Week 12 analysis has a
real signal to recover.
"""

from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 4031
ROW_COUNT = 12000
START = datetime(2026, 5, 29, tzinfo=timezone.utc)
END = datetime(2026, 11, 25, 23, 59, tzinfo=timezone.utc)

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
OUTPUT_DIR = BASE / "output"

CATEGORIES = {
    "scanners and handhelds": {
        "weight": 0.24,
        "median_hours": 5.0,
        "titles": [
            "Scanner will not pair with handheld",
            "Handheld battery drains during shift",
            "Barcode reads fail at packing station",
            "Scanner dock not charging",
            "Handheld screen freezes after login",
        ],
    },
    "dispatch app": {
        "weight": 0.22,
        "median_hours": 8.0,
        "titles": [
            "Dispatch app route will not save",
            "Driver assignment screen loads slowly",
            "Route update does not reach driver",
            "Dispatch map shows stale location",
            "App closes when opening route detail",
        ],
    },
    "printers and labels": {
        "weight": 0.18,
        "median_hours": 4.0,
        "titles": [
            "Label printer jams on outbound orders",
            "Shipping labels print with faded text",
            "Printer queue stuck after label change",
            "Wrong label size on pick tickets",
            "Printer offline in packing area",
        ],
    },
    "logins and access": {
        "weight": 0.14,
        "median_hours": 3.0,
        "titles": [
            "Agent cannot sign in after password reset",
            "New hire account missing desk access",
            "Login loops back to sign in page",
            "Access removed after role change",
            "Multi factor prompt not arriving",
        ],
    },
    "network": {
        "weight": 0.12,
        "median_hours": 12.0,
        "titles": [
            "Warehouse Wi Fi drops near dock doors",
            "Network latency during peak sort",
            "VPN connection fails for remote agent",
            "Access point offline in aisle twelve",
            "Intermittent packet loss on support VLAN",
        ],
    },
    "warehouse systems": {
        "weight": 0.10,
        "median_hours": 18.0,
        "titles": [
            "Inventory count does not match shelf scan",
            "Pick task stuck after item move",
            "Warehouse dashboard totals lag behind scans",
            "Order status not updating after pack",
            "Cycle count import fails validation",
        ],
    },
}


def choose_created_at(rng: np.random.Generator) -> datetime:
    total_days = (END.date() - START.date()).days + 1
    day_weights = []
    for day_index in range(total_days):
        day = START + timedelta(days=day_index)
        growth = 1.0 + (0.35 * day_index / max(total_days - 1, 1))
        weekday_weight = 1.0 if day.weekday() < 5 else 0.38
        day_weights.append(growth * weekday_weight)
    day_weights = np.array(day_weights, dtype=float)
    day_weights = day_weights / day_weights.sum()
    day_index = int(rng.choice(total_days, p=day_weights))

    hour_weights = np.array(
        [0.4, 0.3, 0.25, 0.25, 0.35, 0.7, 1.4, 2.2, 3.0, 3.4, 3.2, 3.0, 2.7, 3.0, 3.1, 2.8, 2.2, 1.6, 1.1, 0.8, 0.65, 0.55, 0.5, 0.45],
        dtype=float,
    )
    hour_weights = hour_weights / hour_weights.sum()
    hour = int(rng.choice(24, p=hour_weights))
    minute = int(rng.integers(0, 60))
    return START + timedelta(days=day_index, hours=hour, minutes=minute)


def main() -> None:
    rng = np.random.default_rng(SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    category_names = list(CATEGORIES)
    category_weights = np.array([CATEGORIES[name]["weight"] for name in category_names], dtype=float)
    category_weights = category_weights / category_weights.sum()

    rows = []
    for incident_id in range(1, ROW_COUNT + 1):
        category = str(rng.choice(category_names, p=category_weights))
        spec = CATEGORIES[category]
        title = str(rng.choice(spec["titles"]))
        created_at = choose_created_at(rng)

        median_hours = float(spec["median_hours"])
        resolution_hours = float(rng.lognormal(mean=np.log(median_hours), sigma=0.85))
        resolution_hours = min(max(resolution_hours, 0.25), 240.0)
        resolved_candidate = created_at + timedelta(hours=resolution_hours)
        age_days = (END - created_at).days

        if age_days > 14:
            closed_probability = 0.97
        elif age_days >= 3:
            closed_probability = 0.85
        else:
            closed_probability = 0.55

        is_closed = bool(rng.random() < closed_probability) and resolved_candidate <= END
        if is_closed:
            status = "closed"
            resolved_at = resolved_candidate
            stored_resolution = round(resolution_hours, 2)
        else:
            status = "in_progress" if rng.random() < 0.55 else "open"
            resolved_at = pd.NaT
            stored_resolution = np.nan

        rows.append(
            {
                "incident_id": incident_id,
                "title": title,
                "description": "Synthetic support incident generated for INET 4031 Week 11 kickoff.",
                "category": category,
                "status": status,
                "created_at": created_at.isoformat(),
                "resolved_at": "" if pd.isna(resolved_at) else resolved_at.isoformat(),
                "resolution_hours": "" if pd.isna(stored_resolution) else stored_resolution,
                "source_system": "synthetic_generator",
                "synthetic": True,
            }
        )

    frame = pd.DataFrame(rows).sort_values(["created_at", "incident_id"]).reset_index(drop=True)
    frame["incident_id"] = range(1, len(frame) + 1)
    data_path = DATA_DIR / "generated_incidents.csv"
    frame.to_csv(data_path, index=False)

    written = pd.read_csv(data_path, dtype=str, keep_default_na=False)
    created = pd.to_datetime(written["created_at"], utc=True, format="ISO8601")
    resolved = pd.to_datetime(written["resolved_at"].replace("", pd.NA), utc=True, errors="coerce", format="ISO8601")
    closed = frame["status"].eq("closed")
    quality_rows = [
        {"metric": "row_count", "value": int(len(frame)), "expected": ">=10000", "status": "PASS" if len(frame) >= 10000 else "FAIL"},
        {"metric": "date_range_days", "value": int((created.max() - created.min()).days + 1), "expected": ">=90", "status": "PASS" if (created.max() - created.min()).days + 1 >= 90 else "FAIL"},
        {"metric": "min_created_at", "value": created.min().isoformat(), "expected": "present", "status": "PASS"},
        {"metric": "max_created_at", "value": created.max().isoformat(), "expected": "present", "status": "PASS"},
        {"metric": "category_null_count", "value": int(frame["category"].isna().sum() + frame["category"].eq("").sum()), "expected": "0", "status": "PASS" if frame["category"].notna().all() and frame["category"].ne("").all() else "FAIL"},
        {"metric": "closed_rows", "value": int(closed.sum()), "expected": ">0", "status": "PASS" if closed.sum() > 0 else "FAIL"},
        {"metric": "closed_missing_resolved_at", "value": int(resolved[closed].isna().sum()), "expected": "0", "status": "PASS" if resolved[closed].notna().all() else "FAIL"},
        {"metric": "duplicate_incident_ids", "value": int(frame["incident_id"].duplicated().sum()), "expected": "0", "status": "PASS" if frame["incident_id"].is_unique else "FAIL"},
        {"metric": "synthetic_rows", "value": int(frame["synthetic"].sum()), "expected": str(len(frame)), "status": "PASS" if frame["synthetic"].all() else "FAIL"},
    ]
    for category, count in frame["category"].value_counts().sort_index().items():
        quality_rows.append({"metric": f"category_count_{category}", "value": int(count), "expected": ">0", "status": "PASS" if count > 0 else "FAIL"})

    quality_path = OUTPUT_DIR / "data_quality.csv"
    with quality_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value", "expected", "status"])
        writer.writeheader()
        writer.writerows(quality_rows)

    print(f"Wrote {data_path} with {len(frame)} rows")
    print(f"Wrote {quality_path}")


if __name__ == "__main__":
    main()
