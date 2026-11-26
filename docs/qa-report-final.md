# QA Report Final

Week 11 test cases are drafted before the Week 12 build work. Actual results are updated as evidence is collected.

| ID | Requirement | Test steps | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| TC-01 | Dataset has at least 10000 rows | Run generate_data.py and read data_quality.csv | row_count is at least 10000 | 12000 rows | Pass |
| TC-02 | Dataset covers at least 90 days | Read min and max created_at in data_quality.csv | date_range_days is at least 90 | 181 days | Pass |
| TC-03 | Every row has a category | Check category_null_count in data_quality.csv | category_null_count is 0 | 0 | Pass |
| TC-04 | Every closed row has a resolution time | Check closed_missing_resolved_at in data_quality.csv | closed_missing_resolved_at is 0 | 0 | Pass |
| TC-05 | Control matrix has at least 15 controls | Count rows in control-matrix.csv | Count is at least 15 | 20 controls | Pass |
| TC-06 | Risk register shows before and after remediation | Compare score_before and score_after in risk-register.csv | Every after score is below its before score | All after scores are lower | Pass |
| TC-07 | Evidence script is repeatable | Run collect_evidence.py twice | checks.csv and evidence-index.md are regenerated | Script writes both files | Pass |
| TC-08 | Environment checkpoint is saved | Run environment_checkpoint.sh | environment-checkpoint.txt exists with tool and Git details | Checkpoint file is generated | Pass |
| TC-09 | Cluster checkpoint runs on the Ubuntu k3s VM | Run environment_checkpoint.sh on the VM with kubectl available | Nodes and pods are listed | Needs VM run | Pending |
| TC-10 | No secrets are committed | Run collect_evidence.py secret pattern scan | No secret patterns are found | No secret patterns found | Pass |
| TC-11 | Week 12 analysis outputs regenerate from one command | Run the Week 12 pipeline command when built | Three CSV files and three PNG charts are regenerated | Not built in Week 11 | Pending |
| TC-12 | Statistical check has a number and plain English sentence | Read the Week 12 statistical output | A numeric result and interpretation are saved | Not built in Week 11 | Pending |
