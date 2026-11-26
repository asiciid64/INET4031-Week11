# INET 4031 Week 11 Kickoff

Selected track is Applied Data Science. The business problem is Harborlight Logistics Support Desk staffing. Dana Okafor needs evidence about incident growth, resolution time, and the categories that keep the desk busiest before the next quarterly business review.

This branch establishes the Week 11 kickoff only. It sets up the project structure, working environment, tools, controls, risk documentation, dataset decision, data quality evidence, and evidence collection process for Weeks 12 to 14.

## How to run this

Create the virtual environment and install the Python tools.

```bash
python3 -m venv ~/data-science-venv
~/data-science-venv/bin/pip install --upgrade pip
~/data-science-venv/bin/pip install -r capstone/data-science/requirements.txt
```

Generate the Week 11 dataset and data quality file.

```bash
~/data-science-venv/bin/python capstone/data-science/scripts/generate_data.py
```

Collect evidence and save the environment checkpoint.

```bash
~/data-science-venv/bin/python capstone/data-science/scripts/collect_evidence.py
bash capstone/data-science/scripts/environment_checkpoint.sh
```

The evidence outputs are written under capstone/data-science/evidence. The dataset is written under capstone/data-science/data. The data quality output is written under capstone/data-science/output.

## Week 11 evidence map

Task 1 is covered by this README and capstone/data-science/DATA.md. The selected track is Applied Data Science and the project aligns to the Harborlight staffing problem.

Task 2 is covered by the week11-kickoff branch.

Task 3 is covered by the pull request opened from week11-kickoff after the branch is pushed.

Task 4 is covered by capstone/data-science/scripts/environment_checkpoint.sh and capstone/data-science/evidence/environment-checkpoint.txt.

Task 5 is covered by capstone/data-science/TOOL-VERSIONS.txt and capstone/data-science/requirements.txt.

Task 6 is covered by capstone/data-science/control-matrix.md and capstone/data-science/control-matrix.csv.

Task 7 is covered by capstone/data-science/risk-register.md and capstone/data-science/risk-register.csv.

Task 8 is covered by capstone/data-science/scripts/collect_evidence.py and the files it writes under capstone/data-science/evidence.

## Data safety

All incident data in this kickoff is synthetic. It contains no real customer names, email addresses, or personal data.
