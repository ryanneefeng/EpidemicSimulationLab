# Start here

Day 1 checks that you can edit a scenario and read it with Python. Disease simulation comes next.

## What the folders and files do

| Item | Purpose |
| --- | --- |
| `day1.py` | Our Python code. It reads, checks, and displays scenario settings. |
| `scenarios/example.json` | Editable inputs: population size, age groups, transmission, and mortality. |
| `.vscode/settings.json` | Gives VS Code the default path to this project's Python interpreter. |
| `.vscode/extensions.json` | Recommends the Python and Pylance extensions for editing Python. |
| `.venv/` | Python's generated local environment, including its interpreter and installed packages. |
| `.git/` | Git's internal history and settings. Let Git manage this folder. |
| `.gitignore` | Tells Git which local files to leave out of commits, including `.venv`. |
| `docs/` | Our explanations, plans, progress notes, sources, and attribution. |
| `data/raw/` | A place for future source data downloads. |
| `results/` | A place for future simulation outputs. |
| `.gitkeep` | An empty placeholder so Git can record an otherwise empty folder. |
| `README.md` | The main project introduction and run instructions. |
| `LICENSE` | The MIT terms for sharing and using the project's code. |

For now, focus on `day1.py` and `scenarios/example.json`. You can collapse `.venv` in VS Code's Explorer.

## Why Scripts contains .bat and .ps1 files

Python created `.venv/Scripts` when the environment was installed. Its contents are environment tools, rather than our modeling code.

- `python.exe` runs Python for this project.
- `pip.exe` installs packages into this environment when we need them.
- `activate.bat` selects the environment in Windows Command Prompt.
- `deactivate.bat` undoes that selection in Command Prompt.
- `Activate.ps1` selects the environment in PowerShell.
- `activate` and `activate.fish` support other shells.
- `pythonw.exe` runs Python without opening a console window on Windows.

Activation changes which Python the shell finds when you type `python`. Our run command selects the interpreter directly, so activation is optional. These generated files stay out of Git and usually need no editing. See the [Python environment documentation](https://docs.python.org/3.14/library/venv.html).

## Read the output

Run this from the project folder in VS Code's terminal:

```powershell
.\.venv\Scripts\python.exe day1.py
```

| Output | Meaning |
| --- | --- |
| `Scenario: Day 1 illustrative respiratory-disease scenario` | The name of the example you loaded. Its values are invented for learning. |
| `Loaded settings. No epidemic has been simulated yet.` | The script successfully read and checked the inputs. |
| `Planned population: 200 people` | The future simulation will use this many people. The reader has not created them yet. |
| `Age groups: 0-19, 20-39, 40-59, 60-79, 80+` | The chosen age categories. We have not assigned population counts to them yet. |
| `Transmission per active encounter: 4%` | An infectious person encountering a susceptible person will have a 4-in-100 chance of transmitting infection in the planned model. |
| `Death probability per infection: 5%` | A person who becomes infected will have a 5-in-100 chance of dying from that infection in the planned model. |

An infectious person can transmit disease. A susceptible person can become infected. Later we will also represent people who have been exposed, recovered, or died.

Probabilities describe chances. Actual infections and deaths will depend on encounters and random outcomes. The current output contains inputs; infection and death totals will come from the future simulation.

## Follow the code

1. `argparse` selects the scenario file. With no argument, it uses `scenarios/example.json`.
2. `Path` opens the file, and `json.loads` reads its JSON text into a Python dictionary.
3. Validation checks probability ranges, age boundaries, and population size.
4. The script builds readable age labels and prints the settings.

In the JSON file, `0.04` means 4% and `0.05` means 5%. Age lower bounds `[0, 20, 40, 60, 80]` start each age group; the last group has no upper limit. `illustrative_only` records that this is an invented example.

## Try one change

1. Run the original scenario.
2. Open `scenarios/example.json` and change transmission to `0.20` and mortality to `0.50`.
3. Save, then run the same command again.
4. Find 20% transmission and 50% mortality in the output. The population and age groups should be unchanged.

You have now controlled disease assumptions through an input file. Our next increment will create person records with disease states. After that, we will implement and hand-check the first disease transitions.

## Save each increment

For each assistant change to a project file, verify it, make a separate commit with a short relevant message, and push to the existing GitHub repository. Generated environments and temporary outputs remain ignored.
