# Current project plan

Updated October 12, 2026. Approximately 40 working sessions over 20 active weeks, at 3-4 hours/week (60-80 hours). Sessions are work blocks, not consecutive calendar days.

## Goal

Build a configurable epidemic and vaccine-allocation scenario tool. The midterm is related prior work; its age groups and parameters are examples. Develop understandable terminal inputs, outputs, and mathematics before returning to a browser interface.

Country selection supplies population age shares and contact matrices. Users choose simulation size and hypothetical disease settings. Later browser controls can use sliders for initially infectious count, transmission, and mortality; age-group counts will come from geographic data.

## Milestones

| Weeks | Work | Useful result |
| --- | --- | --- |
| 1-2 | Terminal setup, country datasets, person states, event specification | Country-based starting population and traceable outputs |
| 3-5 | Extend demographic/contact imports, metadata, city inputs | Updated country presets and locality demographic input |
| 6-8 | Stochastic epidemic engine, vaccine supply and basic allocations | Reproducible static-network experiments |
| 9-12 | Persistent relationships, recurring encounters, temporary edges | Changing network with measured mixing and repetition |
| 13-15 | Browser interface, sliders, playback, plots | Interactive display of the verified model |
| 16-18 | Repeated-run comparisons and sensitivity | Infection/death distributions and intervention tradeoffs |
| 19-20 | Validation, explanations, refinements, buffer | Reproducible research prototype |

Aim for a tiny disease simulation before week 6. Each session should add one understandable modeling step. Commit related work at substantial milestones. Operational policy use requires calibration and independent validation beyond this prototype.

## Mathematics

- Person disease states: S, E, I, R, D. Vaccination is recorded separately.
- Transmission is a probability per active encounter; mortality is a probability per infection. Both accept 0-100%.
- Begin with explicit disease timers and toy durations, then add justified distributions.
- Synchronous event order prevents within-step instantaneous infection chains.
- Relationship existence and daily interaction are separate. Fit/check a contact budget across layers.
- Keep national population counts separate from a small synthetic population. Validate age-bin aggregation and contact reciprocity before building networks.
- Show infections and deaths separately. Weighted objectives use explicit user priorities.
- Record configurations, seeds, data versions, and environment. Keep extinction runs and distinguish stochastic variability from parameter uncertainty.
- Check accounting, probability ranges, timers, self/duplicate contacts, vaccine limits, and sensible limiting cases.

## Current state

The terminal accepts country, simulation size, age-group width, initially infectious count, disease probabilities, and seed. It creates individual records and prints day-0 state totals, demographic shares, and an aggregated contact table. The prototype supports 1-10,000 simulated people.

Prepared datasets contain 201 demographic locations and 177 country/area contact matrices. Demographics are 2020 projections from UN WPP 2019, paired with Prem et al. (2021) synthetic contacts. Country selection offers the 177 locations with both inputs. Ten-year groups are the default, ending in 70+ to respect the source 75+ contact group. Original data resolution is preserved.

No disease events have advanced yet. Disease probabilities remain user-selected hypothetical settings. Disease durations, mortality timing, and vaccine eligibility need specification. City data and newer demographic revisions remain future imports.

## Run and next exercise

From C:\endemic-scenerio-lab, run `.\.venv\Scripts\python.exe app.py --example` for immediate output, or `app.py` for interactive questions. See README for setup.

Try Canada with 20 simulated people, three initially infectious, 20% transmission, and 50% mortality. Confirm 17 susceptible and three infectious, and explain why changing disease probabilities does not change day 0. Inspect the country age shares and contact table.

Next: agree on exposed/infectious durations and mortality timing, hand-trace progression on a fixed graph, then implement one synchronous disease-spread step. Data details and aggregation assumptions are in DATA_SOURCES.md.
