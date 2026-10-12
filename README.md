# Epidemic Scenario Lab

A configurable epidemic and vaccine-allocation modeling project. Age groups, disease parameters, demographics, contact data, and vaccination strategies will be editable. The midterm paper is related prior work; its choices are not fixed requirements.

## Day 1 in VS Code

1. Choose **File > Open Folder** and open this repository.
2. Choose **Terminal > New Terminal**.
3. Create a local Python environment:

```powershell
py -V:3.14 -m venv .venv
```

4. Press **Ctrl+Shift+P**, choose **Python: Select Interpreter**, and select `.venv\Scripts\python.exe`.
5. Run:

```powershell
.\.venv\Scripts\python.exe day1.py
```

Python 3.14.5 was used to check this starter. No third-party packages are needed. Calling the executable directly avoids needing to activate the environment.

Expected output includes:

```text
Simulated population: 200
Age groups: 0-19, 20-39, 40-59, 60-79, 80+
Transmission per active encounter: 4%
Death probability per infection: 5%
```

This first script loads and checks settings. The disease engine, vaccine allocation, data import, and interactive interface come in later increments.

## First exercise

Open `scenarios/example.json`. Change transmission from `0.04` to `0.20` and mortality from `0.05` to `0.50`. Rerun to see 20% and 50%. Probabilities use fractions: `0.05` means 5%; `5` is invalid.

Age lower bounds `[0, 20, 40, 60, 80]` describe groups 0-19, 20-39, 40-59, 60-79, and 80+. These groups are examples and can be changed. Real data will require compatible source bins.

You can load another scenario:

```powershell
.\.venv\Scripts\python.exe day1.py scenarios/example.json
```

Read `day1.py` from top to bottom: arguments select the file, JSON becomes a dictionary, validation checks inputs, and print statements show settings. Next session introduces person states and event timing.

## Save progress

Your public repository is https://github.com/ryanneefeng/epidemic-scenario-lab . The existing MIT license is preserved.

```powershell
git diff
git add scenarios/example.json
git commit -m "Explore transmission and mortality scenario inputs"
git push
```

Code, scenario files, and documentation belong in Git. Local environments, raw downloads, and generated results are ignored.

## Project files

- `day1.py`: runnable scenario reader.
- `scenarios/`: editable inputs.
- `docs/PROJECT_PLAN.md`: milestones and modeling assumptions.
- `docs/SESSION_LOG.md`: progress and exercises.
- `docs/DATA_SOURCES.md`: contact and demographic import requirements.
- `docs/ATTRIBUTION.md`: original team and new contributions.
- `data/raw/` and `results/`: local data and outputs.
