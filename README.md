# Epidemic Simulation Lab

## Abstract

This applied mathematics project studies how age mixing and hypothetical disease parameters affect epidemic outcomes, with vaccine allocation as a later extension. A daily stochastic susceptible-exposed-infectious-recovered-dead (SEIRD) model combines country age distributions with synthetic contact matrices. The Day 2 baseline provides individual disease states and timers, synchronous disease progression, and reproducible terminal experiments. Its purpose is to make assumptions and their consequences inspectable before introducing vaccine policies.

An illustrative 80-run experiment compares 4% and 20% per-encounter transmission with 5% and 50% mortality per infection. At 4% transmission, some introductions cause no secondary cases while others spread widely. These results describe this small hypothetical model; they are not estimates for a particular pathogen or country-wide forecasts.

## Authorship and modeling responsibility

**The majority of this codebase was built through working with OpenAI Codex. Ryan Feng independently conceived and approved the mathematical backbone, research-data selection, and modeling direction.** Codex contributed implementation, debugging, tests, derivations, and documentation under Ryan's direction. The related midterm paper retains its original authors' contributions; see [attribution](docs/ATTRIBUTION.md).

Ryan explicitly approved the 75+ age approximation below. New Day 2 implementation choices—Poisson exposure opportunities, fixed disease durations, and mortality at infectious exit—are **provisional working assumptions for review**, rather than claims of prior approval or empirical calibration.

## 1. Research question and scope

How do per-encounter transmission and mortality change total infections and deaths when country age composition and contact patterns are held fixed? Establishing this baseline is necessary before asking how limited vaccines should be distributed.

Each simulated person occupies one of five states: susceptible ($S$), exposed but not infectious ($E$), infectious ($I$), recovered and immune ($R$), or dead ($D$). All people start unvaccinated. The current model has no vaccine allocation, explicit social network, reinfection, births, aging, migration, or behavior change. It is a closed population over a user-selected time horizon.

## 2. Country data and age structure

The committed demographic file contains 201 country/area rows with both-sex population counts for 1 July 2020, from UN World Population Prospects 2019, Rev. 1, as distributed in the [research repository's population input](https://github.com/kieshaprem/synthetic-contact-matrices/blob/7fcb6985dbc3070cdcb3e5daa5f6b26ce2605d69/generate_synthetic_matrices/input/pop/popage_total2020.csv). Source thousands are converted to people; five-year bins through 100+ remain in `data/demographics.csv`.

The contact data provides 177 complete 16-by-16 matrices from [Prem et al. (2021)](https://doi.org/10.1371/journal.pcbi.1009098). We select overall geography and all contact locations. Entry $C_{ab}$ is the mean number of daily contacts an age-$a$ participant has with age-$b$ people. These are synthetic estimates, not observed relationships between our simulated individuals. Country selection uses the 177 locations with both inputs.

### The approved 75+ approximation

Although the source CSV labels its last bin 75+, the [2024 correction](https://doi.org/10.1371/journal.pcbi.1012454) identifies an age-80 coverage limit. We interpret that native bin as 75-79 and reuse its final row **and** column unchanged for one combined **75+** group. All demographic counts from age 75 through 100+ are included. We do not duplicate the final contact column or multiply its rates by the added population. Contact behavior above age 79 is therefore approximated.

Five-year modeled groups end in 75+. Optional ten-year groups end in 70+, and twenty-year groups end in 60+; both combine the same underlying 75+ bin with younger bins. Ten-year groups are the default. This dataset cannot provide independent contact rates for an 80+ group.

### Aggregation and population scaling

Write $P_a$ for a country's population in source group $a$, after the 75+ extension. For broader participant group $A$ and contact group $B$:

$$
P_A=\sum_{a\in A}P_a,\qquad
C_{AB}=\frac{\sum_{a\in A}P_a\sum_{b\in B}C_{ab}}{P_A}.
$$

Thus contact columns add and participant rows are population-weighted averages. This preserves population-weighted total contact volume under the extended demographic weights. It does not establish empirical rates for older adults or enforce contact reciprocity.

For a simulation of $N$ people, the ideal allocation is $n_A^*=NP_A/\sum_B P_B$. We first take $\lfloor n_A^*\rfloor$, then allocate the remaining people to the largest fractional remainders, breaking ties by age order. Consequently $\sum_A n_A=N$. Small groups can round to zero; their contact opportunities are omitted. National counts and simulated counts remain distinct. Per-person contact rates are retained when reducing population size, so a small simulation is a mixing approximation, not a scaled national forecast.

Pinned source versions, checksums, transformations, and licenses are in [data/SOURCES.json](data/SOURCES.json), [data details](docs/DATA_SOURCES.md), and `data/LICENSE`.

## 3. Daily infection probability

Let $p$ denote transmission probability per encounter, and $I_j(t)$ the infectious count in modeled group $j$ at the start of day $t$. For a susceptible person in group $i$, the potential contact pool in group $j$ has size $m_{ij}=n_j-\mathbf{1}_{i=j}$: a person cannot contact themself. For a one-day step:

$$
\mu_i(t)=\sum_{j:m_{ij}>0}C_{ij}\frac{I_j(t)}{m_{ij}},\qquad
q_i(t)=1-\exp[-p\mu_i(t)].
$$

Here $\mu_i$ is expected infectious exposure opportunities per day, while $q_i$ is a daily infection probability. We assume those opportunities are independent Poisson events. Using the [Poisson probability mass function](https://itl.nist.gov/div898/handbook/eda/section3/eda366j.htm), for $K\sim\mathrm{Poisson}(\mu_i)$:

$$
P(\text{no infection})=\sum_{k=0}^{\infty}(1-p)^k e^{-\mu_i}\frac{\mu_i^k}{k!}
=e^{-p\mu_i}.
$$

Conditional on the start-of-day population, susceptible people receive independent Bernoulli draws with probability $q_i$. Equivalently, new exposures in group $i$ satisfy $X_i(t)\sim\mathrm{Binomial}(S_i(t),q_i(t))$. The implementation evaluates the exponential expression directly; it does not generate contact edges. At $p=1$, infection still requires an encounter. At $p=0$, zero contacts, or zero infectious people, new infections are impossible.

**Fixed contact-pool assumption:** $n_j$ retains its original size after deaths. Opportunities directed toward dead people are lost, not redistributed to living people. Recovered people are noninfectious and immune. With the same infectious duration for every outcome, changing mortality therefore does not change exposure pressure. This simplifies the first sensitivity study; a model of contact redistribution or earlier fatal outcomes could behave differently.

## 4. Disease timing and accounting

| Setting | Example | Interpretation |
| --- | --- | --- |
| $N$ | 200 | Simulated people, allocated using country age shares |
| $I(0)$ | 1 | Uniformly sampled initial infectious people |
| $p$ | 0.04 | Transmission probability per encounter |
| $f$ | 0.05 | Probability an infection ultimately ends in death |
| $L$ | 2 days | Fixed exposed period before infectiousness |
| $T_I$ | 5 days | Fixed infectious period before recovery or death |
| Horizon | 60 days | Maximum duration of a normal example run |
| Seed | 42 | Reproducible random realization |

All disease settings are hypothetical, editable inputs. The program accepts probabilities from 0% to 100%, populations from 1 to 10,000, and whole-day durations/horizons from 1 to 3,650. These numerical bounds are input limits, not claims of biological plausibility. Initially infectious people start at the beginning of their infectious period. Everyone else begins susceptible.

Each day first calculates exposures from the old population, then applies all changes at the boundary. A new exposure enters $E$ with timer zero and cannot progress again that day. Existing exposed people enter $I$ after $L$ full daily intervals; existing infectious people resolve after $T_I$ intervals. On resolution, one Bernoulli($f$) draw determines death; otherwise the person recovers. Mortality is not applied as a daily probability.

Let $X$ count new exposures, $Y$ exposed-to-infectious transitions, $Z$ infectious exits, and $W$ fatal exits during an interval. Summing across ages:

$$
\begin{aligned}
S(t+1)&=S(t)-X,\\
E(t+1)&=E(t)+X-Y,\\
I(t+1)&=I(t)+Y-Z,\\
R(t+1)&=R(t)+Z-W,\\
D(t+1)&=D(t)+W,\qquad W\mid Z\sim\mathrm{Binomial}(Z,f).
\end{aligned}
$$

These equations conserve $S+E+I+R+D=N$. Timers determine $Y$ and $Z$; constant daily recovery hazards are not used. Recovered and dead states are absorbing.

For a hand check with $L=2$, $T_I=3$, and $f=0$, a person exposed at the end of day 1 has states $E,E,I,I,I,R$ on days 1 through 6. An initially infectious person recovers at the end of day 3. This trace is tested directly.

## 5. Numerical experiment and results

The Day 2 study uses the United States preset, $N=200$, ten-year groups, $I(0)=1$, $L=2$, $T_I=5$, and a 120-day horizon. It crosses $p\in\{0.04,0.20\}$ with $f\in\{0.05,0.50\}$, retaining all 20 seeds (0-19) per combination, including early extinctions. The same seeds are paired across combinations. Initialization, transmission, and fatal outcomes use separate local random streams.

Attack percentage is $100[N-S(t)]/N$, including initial cases. Peak infectious count is the largest recorded $I(t)$; ties use the first day. The run stops at the horizon or when $E+I=0$. Infections still exposed or infectious at the horizon are reported as unresolved, so deaths at that point are incomplete outcomes.

For replicate measurements $x_1,\ldots,x_M$, we report the sample mean, sample standard deviation (SD), and Monte Carlo standard error (MCSE):

$$
\bar{x}=\frac{1}{M}\sum_{r=1}^M x_r,\qquad
s^2=\frac{1}{M-1}\sum_{r=1}^M(x_r-\bar{x})^2,\qquad
\mathrm{MCSE}=\frac{s}{\sqrt{M}}.
$$

SD describes variation between runs. MCSE describes simulation uncertainty in the estimated mean at fixed inputs; it excludes uncertainty about disease parameters, contact estimates, and model assumptions. Cells share seeds, so comparisons should account for pairing rather than assume independent cells.

Results generated October 14, 2026 with Python 3.14.5, implementation milestone `a26f6df`:

| Transmission | Mortality | Attack % mean / SD / MCSE | Deaths mean / SD / MCSE | No secondary infections | Unresolved runs |
| --- | --- | --- | --- | --- | --- |
| 4% | 5% | 63.60 / 42.42 / 9.49 | 6.95 / 5.23 / 1.17 | 6/20 | 0/20 |
| 4% | 50% | 63.60 / 42.42 / 9.49 | 64.20 / 43.16 / 9.65 | 6/20 | 0/20 |
| 20% | 5% | 100.00 / 0.00 / 0.00 | 11.15 / 2.46 / 0.55 | 0/20 | 0/20 |
| 20% | 50% | 100.00 / 0.00 / 0.00 | 101.15 / 7.34 / 1.64 | 0/20 | 0/20 |

At 4% transmission, the large attack-rate SD reflects substantial variation, including six introductions with no onward spread. The mean alone is inadequate. Every sampled 20% run infected all 200 people; zero sampled variation does not prove a deterministic outcome for other seeds or settings. Equal attack statistics between mortality settings follow from the fixed infectious duration and fixed contact pools, and are verified with paired-run tests. The higher mortality setting changes deaths without changing the infection trajectories in this model.

For comparison, the single default run (seed 42, 60-day horizon) produces 173 infections, 7 deaths, and a peak of 49 infectious people on day 26. It becomes disease-free on day 54. A configured 5% mortality does not require exactly 5% of infections to die in each realization.

The study's `replicates.csv` SHA-256 is `ee51772791be9ecf48022ff59cdf18215da59c20ff6f5e1e45dea567fe514470`. Reproduce the table with the command below; saved metadata includes actual input matrices, settings, seeds, Python version, and source/data file hashes.

## 6. Verification and limitations

The 33 automated checks cover source checksums, all 177 countries at three age resolutions, population rounding, contact aggregation, analytic Poisson probabilities, a hand-traced disease course, no instantaneous chains, state/flow conservation, limiting probabilities, independent random streams, censoring, saved experiment provenance, and terminal operation. A 10,000-person one-day check compares infections with the derived binomial mean and variance. These are mathematical and implementation checks, not external epidemiological validation.

The principal limitations are historical demographics; synthetic contacts; the 75+ proxy; demographic rounding; homogeneous mixing within ages; unbalanced contact reciprocity; fixed durations and age-independent disease probabilities; independent exposure opportunities without repeated partnerships; and the assumption of lost contacts after death. Twenty replicates provide only a small exploratory study. Future work should examine these assumptions and population-size sensitivity before interpreting intervention differences. City-level data, vaccine eligibility/effectiveness, limited supply, and allocation objectives remain to be defined.

## Reproduce in VS Code

Open the project folder, choose **Terminal > New Terminal**, and run:

```powershell
python model.py
```

Answer the questions or press Enter for defaults. Enter percentages as `20` or `50`, not `0.20` or `0.50`. Country selection supplies age shares automatically. The output labels all five states, shows selected daily totals, and reports cumulative infections, deaths, peak infectious count, and any unresolved infections.

| Command | Purpose |
| --- | --- |
| `python model.py --example` | Run the saved example without questions |
| `python model.py --example --country CAN` | Run the example with Canadian demographics and contacts |
| `python model.py --example --contacts` | Also display the aggregated contact matrix |
| `python model.py --list-countries` | List available country codes and names |
| `python model.py --study` | Reproduce the four-cell, 80-run study |
| `python -m unittest discover -s tests -v` | Run verification checks |
| `python prepare_data.py --offline` | Rebuild data from verified cached source downloads |

The code uses only Python's standard library; Python 3.14.5 was tested. Interactive questions require a terminal that accepts input. The program runs offline using committed data. To obtain missing raw source files for rebuilding, use `python prepare_data.py` without `--offline`.

`--study` uses the chosen country's saved population/age/duration settings, overrides transmission and mortality with the four study cells, uses seeds 0-19, and sets the horizon to 120 days. It writes `replicates.csv` and `summary.json` under `results/day2_<COUNTRY>/`. Rerunning replaces those generated files. Results, raw downloads, environments, editor settings, and caches are ignored by Git; the research explanation and reproducible code remain tracked.

`model.py` handles terminal interaction; `src/model.py` defines people and input validation; `src/country_data.py` prepares country presets; `src/simulation.py` implements the equations; `src/experiments.py` repeats and summarizes runs. Example defaults live in `scenarios/example.json`. See [the project plan](docs/PROJECT_PLAN.md) for the next modeling exercise.
