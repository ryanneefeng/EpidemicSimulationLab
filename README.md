# Epidemic Scenario Lab

A configurable epidemic and vaccine-allocation modeling project. Work through the mathematics with terminal inputs and readable outputs. Country data supplies the age distribution.

The majority of the codebase was built through working with OpenAI Codex. Ryan Feng independently conceived and approved the mathematical backbone, research-data selection, and modeling direction. New Day 2 implementation assumptions remain provisional until reviewed; see [attribution](docs/ATTRIBUTION.md).

## Run in VS Code

Open `C:\endemic-scenerio-lab` in VS Code, choose **Terminal > New Terminal**, and run:

```powershell
python model.py
```

Answer each terminal question; press Enter to keep its default. Choose a country, simulated population size, age-group width, initially infectious count, transmission percentage, mortality percentage, and random seed. Age-group population counts are calculated from the selected country. Enter percentages as 20 or 50; the model stores 0.20 or 0.50.

For a quick example with no questions, run `python model.py --example`. It prints results immediately and exits.

For the Day 2 sensitivity study, run `python model.py --study`. It compares 4%/20% transmission and 5%/50% mortality with 20 seeds per combination and a 120-day horizon. It saves replicate results and input checksums under ignored `results/day2_USA/`; rerunning replaces that country's generated study files. `--country CAN` selects another country. Early extinctions remain in the analysis.

List available countries with `python model.py --list-countries`. Run another country's saved example with `python model.py --example --country CAN`. Full country names also work when quoted.

Use the VS Code terminal for interactive questions. An output-only panel cannot accept answers. The program prints its questions directly in the terminal.

Python is already installed on this development machine. The current code uses only Python's standard library, so these commands work without activating `.venv`. Python 3.14.5 was tested. The optional local environment can remain for future dependencies.

## Read the output

The default example creates 200 people with the United States' 2020 age distribution. Whole-person rounding produces 24, 26, 28, 27, 24, 25, 23, and 23 people across the eight groups. Country population counts remain separate from these small simulation counts.

Day 0 contains **199 susceptible, 0 exposed, 1 infectious, 0 recovered, and 0 dead**. The daily SEIRD model then advances until no infections remain or the selected horizon is reached. Exposed and infectious durations are editable whole days (illustrative defaults: 2 and 5). Mortality is sampled once when an infectious period ends; vaccination is not implemented.

The terminal prints selected daily totals, total infections, deaths, and the first peak infectious count. Unresolved infections at the horizon are reported explicitly. Add `--contacts` to display expected daily contacts: participant ages down rows and contacted ages across columns. Those averages determine infection risks through the derivation below.

## Country datasets

| File | Contents |
| --- | --- |
| `data/demographics.csv` | 201 country/area rows; 2020 population counts by five-year age group through 100+. |
| `data/contacts.csv` | 177 country/area contact matrices; 16 by 16, five-year ages ending in 75+. |
| `data/SOURCES.json` | Pinned source versions, checksums, units, and country-name mapping notes. |
| `data/LICENSE` | Upstream GPL-3.0 license for the imported source data. |

These are published historical inputs: UN WPP 2019 revision demographics for 2020, paired with Prem et al. (2021) synthetic contacts. Current population revisions and city data remain future imports. Country selection currently offers the 177 locations with both datasets.

Ten-year groups are the default: 0-9, 10-19, 20-29, 30-39, 40-49, 50-59, 60-69, and 70+. Ryan approved reusing the source 75-79 contact row and column for everyone aged 75+, including all older demographic bins. Five-year groups keep that 75+ group; ten- and twenty-year aggregation end in 70+ and 60+. This is an explicit approximation, since the [source correction](https://doi.org/10.1371/journal.pcbi.1012454) identifies an age-80 coverage limit.

To rebuild the prepared files, run `python prepare_data.py`. It downloads pinned public source files only when absent and verifies their checksums. Use `python prepare_data.py --offline` when those raw files already exist. Raw downloads are ignored by Git and hidden locally in VS Code.

The data comes from [Prem's repository](https://github.com/kieshaprem/synthetic-contact-matrices). See [data details](docs/DATA_SOURCES.md) and [attribution](docs/ATTRIBUTION.md).

## Day 2 transmission derivation

The spread kernel assumes independent Poisson exposure opportunities during each one-day interval. Let $C_{ij}$ be contacts per participant per day, $I_j(t)$ the infectious count, and $n_j$ the initial simulated age-group size. A susceptible person cannot contact themself, so their pool has $n_j-\mathbf{1}_{i=j}$ people. With empty pools contributing zero:

$$\mu_i(t)=\sum_{j:n_j-\mathbf{1}_{i=j}>0} C_{ij}\frac{I_j(t)}{n_j-\mathbf{1}_{i=j}},\qquad q_i(t)=1-\exp[-p\mu_i(t)].$$

Here $p$ is transmission probability per encounter and $q_i$ is infection probability per day. If $K\sim\mathrm{Poisson}(\mu_i)$, then $P(\text{no infection})=E[(1-p)^K]=\exp(-p\mu_i)$. This follows from the [Poisson probability mass function](https://itl.nist.gov/div898/handbook/eda/section3/eda366j.htm); choosing Poisson opportunities is a provisional project assumption. In particular, $p=1$ does not guarantee an encounter.

Pool sizes remain fixed after deaths: opportunities directed toward deceased people are lost rather than reassigned. Empty simulated age groups also lose their contact opportunities. This convention makes mortality affect outcomes but not subsequent exposure pressure when infectious duration is fixed. It is a simplifying assumption, not an empirical behavioral claim.

## Project files and checks

`model.py` starts the program and handles terminal questions and output. `src/model.py` creates person records. `src/country_data.py` loads and combines country data. `prepare_data.py` rebuilds the CSV files. `scenarios/example.json` holds example settings. `tests/` checks the mathematics and terminal behavior; `docs/` explains the plan and sources.

Environment/editor folders and caches are hidden and ignored. Generated Python environment scripts inside `.venv` support the interpreter; they are not project code. The browser prototype was removed from the current files and remains in Git history.

```powershell
python -m unittest discover -s tests -v
```

Related changes are verified together and committed at substantial milestones with a short message, then pushed to https://github.com/ryanneefeng/EpidemicSimulationLab . The next Day 2 milestone compares repeated stochastic runs.
