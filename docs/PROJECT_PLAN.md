# Current project plan

Updated October 12, 2026. Day 1 of approximately 40 working sessions over 20 active weeks, at 3-4 hours/week (60-80 hours). A broader version may take 24 weeks or longer. Sessions are learning/work blocks, not consecutive calendar days.

## Goal and scope correction

Build a configurable epidemic and vaccine-allocation scenario tool, intended for epidemiologists and public-sector analysts. The midterm is related prior work only. Neither its age groups nor its disease parameters are inherited requirements.

Keep disease scenarios, geography/demographics, contact assumptions, vaccination strategies, and simulation/display settings separate. Editable settings first live in versioned configuration files; interface controls will use the same validated inputs. Define transmission as a probability per active encounter and mortality as a probability per infection. Permit 0-100% values, including severe hypothetical scenarios. Later allow age-specific probabilities, time-to-death assumptions, durations, vaccine protection, and waning.

## Milestones

| Weeks | Work | Useful result |
| --- | --- | --- |
| 1-2 | VS Code/Git setup, scenario inputs, person-state/event specification | Editable inputs and a tiny traceable example |
| 3-5 | Demographic/contact file import, metadata, age-bin aggregation | One validated country contact preset and locality demographic input |
| 6-8 | Stochastic epidemic engine, vaccine supply and basic allocations | Reproducible static-network experiments |
| 9-12 | Persistent relationships, recurring encounters, temporary edges | Changing network with measured mixing and repetition |
| 13-15 | Browser interface and visual controls | Play/pause/reset, scenario controls, network and curves |
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
- Created a small configuration reader and documentation; local environment and Git verification are recorded in SESSION_LOG.md.
- Inspected the Prem contact repository structure; no data imported yet.

## Current assumptions and questions

The example JSON is invented. Its five age groups, 4% per-encounter transmission, and 5% mortality are editable demonstrations, not empirical estimates. It does not yet specify age shares, duration distributions, or vaccines. Source age boundaries will constrain supported data aggregation. Mortality's timing and vaccine eligibility must be specified before the engine is implemented.

Public repository: https://github.com/ryanneefeng/epidemic-scenario-lab . The working folder is C:\endemic-scenerio-lab. Python experience is unspecified, so explain code from basics.

## Run and next task

From the repository: `.\.venv\Scripts\python.exe day1.py` (Windows). See README for environment recreation and VS Code interpreter selection.

Learner Day 1 task: run the reader, change 0.04 to 0.20 and 0.05 to 0.50, explain the percentages and units, then commit the change. Day 2: hand-trace S/E/I/R/D progression for 20 people on a fixed graph, then implement one synchronous step. Data milestone next: inspect one real contact file before writing an importer.
