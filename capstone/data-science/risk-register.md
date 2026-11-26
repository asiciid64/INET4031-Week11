# Risk Register

Scores use impact times likelihood on a 1 to 5 scale for each value. Before scores show the risk before kickoff mitigations. After scores show the residual risk after the listed mitigation is in place.

| ID | Risk | Cause | Impact before | Likelihood before | Score before | Mitigation | Impact after | Likelihood after | Score after | Owner | Evidence |
|---|---|---|---:|---:|---:|---|---:|---:|---:|---|---|
| R-01 | Synthetic data does not match real Harborlight patterns | Planted patterns may be stronger or cleaner than real operations | 5 | 4 | 20 | Document planted patterns in DATA.md and state synthetic limits in the final report | 5 | 2 | 10 | Data analyst | DATA.md and risk register |
| R-02 | Category labels are wrong or too broad | Titles may not map cleanly to real work types | 4 | 4 | 16 | Use six defined categories and review category counts and sample titles in evidence | 4 | 2 | 8 | Data analyst | data_quality.csv and generated data review |
| R-03 | Resolution time is mistaken for agent handling time | Elapsed time includes waiting and queue time | 5 | 4 | 20 | State the limit now and require a separate handling time assumption in the staffing model | 5 | 2 | 10 | Data analyst | DATA.md and Week 13 report plan |
| R-04 | Missing resolution times bias the results | Closed rows without resolved times would distort medians and percentiles | 4 | 3 | 12 | Add a data quality gate requiring resolved_at for every closed row | 4 | 1 | 4 | Data analyst | data_quality.csv |
| R-05 | Reseeding creates duplicate rows | Appending generated rows can inflate volume | 4 | 3 | 12 | Generate a fresh CSV from one script and record row counts before analysis | 3 | 1 | 3 | System admin | generate_data.py and data_quality.csv |
| R-06 | Personal data enters shared files | Real names or emails would violate the compliance constraint | 5 | 2 | 10 | Use synthetic generic text only and scan evidence for obvious secret or personal data patterns | 5 | 1 | 5 | Data analyst | generated data and collect_evidence.py |
| R-07 | Secrets are committed to GitHub | Credentials in scripts would expose the VM or database | 5 | 2 | 10 | Keep credentials out of the repo and run a secret pattern check during evidence collection | 5 | 1 | 5 | System admin | collect_evidence.py checks |
| R-08 | Environment cannot be rebuilt | Missing tool versions or manual steps would block Week 13 rebuild | 4 | 4 | 16 | Record requirements and tool versions and save an environment checkpoint | 3 | 2 | 6 | System admin | requirements.txt and TOOL-VERSIONS.txt |
| R-09 | Prometheus history is too short | Metrics may not cover the full incident period | 3 | 4 | 12 | Disclose the Prometheus time range and avoid using it as the main staffing proof | 3 | 2 | 6 | Data analyst | risk register and QA test cases |
| R-10 | Staffing recommendation is overconfident | Small sample effects or wrong handling time assumptions can move the answer | 5 | 3 | 15 | Require assumptions and a 20 percent growth sensitivity check in the final report | 4 | 2 | 8 | Data analyst | QA test cases and Week 13 report plan |
| R-11 | Analysis uses too many shared resources | Heavy tools could slow the single server or shared VM | 3 | 3 | 9 | Run analysis from the venv on the host and avoid always on heavy services | 2 | 1 | 2 | System admin | environment checkpoint |
| R-12 | Branch work bypasses review | Direct changes to main would weaken traceability | 4 | 2 | 8 | Use week11-kickoff and a pull request for review before merge | 3 | 1 | 3 | Project owner | Git branch and pull request |
| R-13 | Tool versions drift between runs | Different package versions can change outputs | 3 | 3 | 9 | Pin the installed environment in requirements.txt and record versions | 2 | 1 | 2 | System admin | requirements.txt |
| R-14 | Database load damages existing tickets | Bulk loading generated rows without backup could corrupt course data | 5 | 2 | 10 | Analyze from CSV for kickoff and require backup before any later bulk load | 4 | 1 | 4 | System admin | DATA.md and control DS-16 |

The largest score reductions come from data quality gates, synthetic data disclosure, fixed seed reproducibility, and the rule that resolution time is not treated as agent handling time.
