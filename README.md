# Epidemic Scenario Lab

A configurable epidemic and vaccine-allocation modeling project. Choose disease and population settings in a browser. Develop the mathematics in small, understandable increments.

## Run in VS Code

Open this folder and choose **Terminal > New Terminal**. Run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:8000** in your browser. Keep the terminal running; **Ctrl+C** stops the app. If the port is occupied, run `app.py --port 8001` and use the printed address.

The environment already exists on the development machine. After a fresh clone, create it with `py -V:3.14 -m venv .venv`, then select `.venv\Scripts\python.exe` using **Python: Select Interpreter** in VS Code. Python 3.14.5 was tested; no third-party packages are needed.

## Current step: user inputs and person records

Enter the population, initially infectious count, age boundaries, age-group population counts, transmission percentage, mortality percentage, and random seed. Select **Create population**.

- Enter percentages as 4 or 50 in the form. The model stores them as fractions, 0.04 or 0.50.
- Age-group counts must add up to the population. The equal-split button creates an illustrative toy distribution; you can replace every count.
- The model creates a separate record for each person, with an ID, age group, disease state, and vaccination status. It currently assigns age groups rather than exact ages.
- Initially infectious people are selected with a local random generator. Identical settings and seed reproduce that selection.
- **Download scenario** exports the settings used to create the displayed population. Editing the form clears the previous result until you create it again.

For the default 200-person example with one initially infectious person, the starting state is **199 susceptible, 0 exposed, 1 infectious, 0 recovered, 0 dead**. S, E, I, R, and D stand for those five states. All people start unvaccinated.

This increment initializes day 0. Transmission and mortality are recorded inputs for the upcoming disease-spread step. Days, infections, recoveries, deaths, and vaccines have not been advanced yet. The prototype supports 1–10,000 people and does not import country/city data yet.

## Clean project layout

| Path | Purpose |
| --- | --- |
| `app.py` | Starts the local server. |
| `src/model.py` | Validates settings and creates person records. |
| `web/index.html` | The browser form and result display. |
| `scenarios/example.json` | Versioned example settings; edit inputs through the browser during normal use. |
| `tests/` | Population accounting and reproducibility checks. |
| `docs/` | Project plan, data-source requirements, and attribution. |

`.venv`, `.vscode`, caches, secrets, and generated outputs are ignored by Git. Local VS Code settings also hide environment and editor folders in Explorer. The `.bat` and `.ps1` scripts inside `.venv` are generated Python environment helpers. Our run command uses the interpreter directly, so activation is optional. See [Python environments](https://docs.python.org/3.14/library/venv.html).

The old Day 1 reader, duplicate walkthrough/progress documents, and empty data/output placeholders have been removed. Their history remains in Git. Useful source code, examples, tests, planning, and attribution stay tracked.

## Verification and progress

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Checks cover population totals, age distributions, initial infection limits, repeatable seeds, independent randomness, and invalid inputs. Browser checks cover creation, custom settings, count errors, reset, equal splitting, and scenario download.

Related changes are verified together, then committed at substantial milestones with a short relevant message and pushed to https://github.com/ryanneefeng/epidemic-scenario-lab . Local ignored settings stay on the development machine.

Next: define disease timers and one synchronous disease-spread step. See [the project plan](docs/PROJECT_PLAN.md), [data sources](docs/DATA_SOURCES.md), and [attribution](docs/ATTRIBUTION.md). The midterm paper is reference material; its parameters and age groups are not requirements for this project.
