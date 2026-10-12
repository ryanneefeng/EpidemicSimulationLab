# Epidemic Scenario Lab

A configurable epidemic and vaccine-allocation modeling project. Work through the mathematics with terminal inputs and readable outputs. Country data supplies the age distribution.

## Run in VS Code

Choose **Terminal > New Terminal**, then run this first example:

```powershell
Set-Location "C:\endemic-scenerio-lab"
.\.venv\Scripts\python.exe app.py --example
```

It prints results immediately and exits. No browser or local server is needed.

To enter your own settings, run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Answer each terminal question; press Enter to keep its default. Choose a country, simulated population size, age-group width, initially infectious count, transmission percentage, mortality percentage, and random seed. Age-group population counts are calculated from the selected country. Enter percentages as 20 or 50; the model stores 0.20 or 0.50.

List the available countries with `app.py --list-countries`. Run a saved example for another country with `app.py --example --country CAN`. Full country names also work when quoted.

Use the VS Code terminal for interactive questions. An output-only panel cannot accept answers. If a previous browser server is still running in a terminal, press Ctrl+C before running this version. The old localhost link is no longer used.

The existing `.venv` works on this development machine. After a fresh clone, create it with `py -V:3.14 -m venv .venv`, then select `.venv\Scripts\python.exe` using **Python: Select Interpreter**. Python 3.14.5 was tested. All code uses Python's standard library.

## Read the output

The default example creates 200 people with the United States' 2020 age distribution. Whole-person rounding produces 24, 26, 28, 27, 24, 25, 23, and 23 people across the eight groups. Country population counts remain separate from these small simulation counts.

Day 0 contains **199 susceptible, 0 exposed, 1 infectious, 0 recovered, and 0 dead**. Everyone starts unvaccinated. Disease probabilities are stored inputs; transmission, recovery, death, and vaccine events come in the next modeling steps.

The contact table shows expected daily contacts: participant ages down the rows, contacted ages across the columns. A decimal value is an average over people. These averages will guide later encounters; they are not infection probabilities or a list of unique relationships.

## Country datasets

| File | Contents |
| --- | --- |
| `data/demographics.csv` | 201 country/area rows; 2020 population counts by five-year age group through 100+. |
| `data/contacts.csv` | 177 country/area contact matrices; 16 by 16, five-year ages ending in 75+. |
| `data/SOURCES.json` | Pinned source versions, checksums, units, and country-name mapping notes. |
| `data/LICENSE` | Upstream GPL-3.0 license for the imported source data. |

These are published historical inputs: UN WPP 2019 revision demographics for 2020, paired with Prem et al. (2021) synthetic contacts. Current population revisions and city data remain future imports. Country selection currently offers the 177 locations with both datasets.

Ten-year groups are the default: 0-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, and 70+. The final group respects the source contact data's 75+ limit. Five-year groups keep 75+; twenty-year groups end in 60+. Original demographic bins remain in the CSV.

To rebuild the prepared files, run `.\.venv\Scripts\python.exe prepare_data.py`. It downloads pinned public source files only when absent and verifies their checksums. Use `prepare_data.py --offline` when those raw files already exist. Raw downloads are ignored by Git and hidden locally in VS Code.

The data comes from [Prem's repository](https://github.com/kieshaprem/synthetic-contact-matrices). See [data details](docs/DATA_SOURCES.md) and [attribution](docs/ATTRIBUTION.md).

## Project files and checks

`app.py` handles terminal questions and output. `src/model.py` creates person records. `src/country_data.py` loads and combines country data. `prepare_data.py` rebuilds the CSV files. `scenarios/example.json` holds example settings. `tests/` checks the mathematics and terminal behavior; `docs/` explains the plan and sources.

Environment/editor folders and caches are hidden and ignored. Generated Python environment scripts inside `.venv` support the interpreter; they are not project code. The browser prototype was removed from the current files and remains in Git history.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Related changes are verified together and committed at substantial milestones with a short message, then pushed to https://github.com/ryanneefeng/epidemic-scenario-lab . Next: define disease durations and one synchronous spread step. See [the plan](docs/PROJECT_PLAN.md).
