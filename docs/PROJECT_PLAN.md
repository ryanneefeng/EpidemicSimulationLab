# Current project plan

Updated October 12, 2026. Day 1 of approximately 40 working sessions over 20 active weeks, at 3-4 hours/week (60-80 hours). A broader version may take 24 weeks or longer. Sessions are learning/work blocks, not consecutive calendar days.

## Goal and scope correction

Build a configurable epidemic and vaccine-allocation scenario tool, intended for epidemiologists and public-sector analysts. The midterm is related prior work only. Neither its age groups nor its disease parameters are inherited requirements.

Keep disease scenarios, geography/demographics, contact assumptions, vaccination strategies, and simulation/display settings separate. Choose settings in the browser form and download them as JSON. Versioned examples use the same validation. Define transmission as a probability per active encounter and mortality as a probability per infection. Permit 0-100% values, including severe hypothetical scenarios. Later allow age-specific probabilities, time-to-death assumptions, durations, vaccine protection, and waning.

## Milestones

| Weeks | Work | Useful result |
| --- | --- | --- |
| 1-2 | VS Code/Git setup, browser inputs, person records, event specification | Editable inputs and a tiny traceable example |
| 3-5 | Demographic/contact file import, metadata, age-bin aggregation | One validated country contact preset and locality demographic input |
| 6-8 | Stochastic epidemic engine, vaccine supply and basic allocations | Reproducible static-network experiments |
| 9-12 | Persistent relationships, recurring encounters, temporary edges | Changing network with measured mixing and repetition |
| 13-15 | Extend the browser with simulation controls and plots | Play/pause/reset, network and curves |
| 16-18 | Repeated-run comparisons and sensitivity | Infection/death distributions; documented intervention tradeoffs |
| 19-20 | Validation, explanations, refinements, buffer | First useful research prototype with reproducible runs |

Aim for a tiny disease simulation earlier than week 6 while the import pipeline develops; the table describes milestone completion, not a delay before code can run. At each session make one small working increment. Later extensions: broader geography, detailed setting-specific network calibration, 12-month waning/reinfection scenarios, larger populations, optimization, and polished deployment. Calibration and independent validation for operational policy use add work beyond this prototype.

## Mathematical commitments

- Person disease states: S, E, I, R, D. Vaccination is separate and persists in records after breakthrough infection.
- Begin with explicit timers and toy durations; add justified duration distributions. Do not silently replace durations with geometric/exponential waits.
- Synchronous event order prevents within-step instantaneous infection chains. Playback speed does not change mathematical step size.
- Relationship existence and daily interaction are separate. Temporary ties form/expire independently of animation. Fit/check a contact budget across layers.
- Start with 200-500 simulated people; retain geography's original population data separately. Rendering and population representation are distinct. No extrapolation by multiplying toy outcomes.
- Show infections and deaths separately. Any weighted objective has explicit user priorities.
- Record configurations, seeds, independent random streams, input versions, and software environment. Keep extinction runs. Separate stochastic variability, uncertainty in estimated means, and parameter sensitivity.
- Validate accounting, probability ranges, timers, self/duplicate contacts, vaccine limits, and sensible limiting cases.

## Completed

- Reviewed the original paper and appendix; preserved team attribution.
- Revised scope after the user clarified configurable disease/age inputs and geographic importing as central requirements.
- Confirmed Python 3.14.5, Git, VS Code, and the Python extension are installed.
- Added a local browser form for editable population, age groups, disease probabilities, and random seed.
- Created individual person records and reproducible initial infectious selections; checked population accounting and invalid inputs.
- Verified the browser form, error messages, reset, equal splitting, and scenario download.
- Consolidated setup instructions in README; ignored local editor settings and generated folders. Git records progress at substantial milestones.
- Inspected the Prem contact repository structure; no data imported yet.

## Current assumptions and questions

The example JSON is invented. Its five equally populated age groups, 4% per-encounter transmission, and 5% mortality are editable demonstrations, not empirical estimates. Users choose age-group counts directly; real demographic importing comes later. Disease durations, mortality timing, and vaccine eligibility still need specification. Source age boundaries will constrain supported data aggregation.

The current model creates day 0 only. Transmission and mortality are saved settings; no disease events have advanced. The form supports up to 10,000 people for this prototype.

Public repository: https://github.com/ryanneefeng/epidemic-scenario-lab . The working folder is C:\endemic-scenerio-lab. Python experience is unspecified, so explain code from basics.

## Run and next task

From the repository: `.\.venv\Scripts\python.exe app.py` (Windows), then open http://127.0.0.1:8000 . See README for environment recreation and VS Code interpreter selection.

Current learning task: create 20 people in the browser, choose age-group counts totaling 20, and set three initially infectious people. Confirm 17 susceptible and three infectious. Change transmission to 20% and mortality to 50%; explain why the initial totals stay the same.

Next: define disease timers and hand-trace S/E/I/R/D progression on a fixed graph, then implement one synchronous step. Data milestone: inspect one real contact file before writing an importer.
