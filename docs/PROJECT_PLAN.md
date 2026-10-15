# Project plan

Updated October 14, 2026. This is an applied mathematics project. Progress is measured by understandable, verified modeling decisions and reproducible results.

## Completed

| Session | Modeling milestone |
| --- | --- |
| Day 1 | Terminal inputs, person states, country demographics, contact data, aggregation, and traceable sources |
| Day 2 | Approved 75+ approximation; fixed disease timers; Poisson daily infection risk; synchronous SEIRD simulation; repeated-run sensitivity study; paper-style README and authorship disclosure |

The terminal accepts country, simulation size, age width, initial infectious count, transmission, mortality, seed, stage durations, and horizon. It reports disease progression and outcomes. The example remains `python model.py`; `--example` runs without questions and `--study` reproduces the first numerical comparison.

## Next modeling session

1. Review the provisional assumptions with Ryan: fixed disease durations, daily Poisson opportunities, mortality at infectious exit, and contact opportunities lost after death.
2. Hand-calculate a small example and compare it with the implementation. Explain why changing mortality alone leaves the infection curve unchanged in this baseline.
3. Test how population size and age resolution affect stochastic extinction and rounding. Compare enough seeds to make uncertainty visible.
4. Define the first vaccine experiment: eligibility, dose supply, timing, effectiveness against infection versus death, and an explicit outcome objective. Implement only after those meanings are clear.

The contact data's final source row and column represent 75-79. Ryan approved applying them to one 75+ group with all older demographic counts retained. Five-year models end in 75+; wider groups combine that bin. This is an approximation to retain in all reports.

## Later work

Extend to age-specific disease risks, justified duration distributions, modern demographic revisions, and city inputs. Decide whether persistent relationships are necessary; if introducing undirected networks, first address contact reciprocity and repeated-contact assumptions. Add vaccine allocation comparisons, then a browser interface once the mathematics and terminal workflow are stable.

The earlier estimate of roughly 40 working sessions / 60-80 hours remains provisional. The interface and network work should follow modeling needs rather than a fixed calendar. Keep substantial changes in meaningful commits, with concise comments and validation of the mathematical behavior.

## Research record

The README contains equations, results, sources, and limitations. DATA_SOURCES.md explains transformations; ATTRIBUTION.md records human and Codex contributions. Each study saves settings, seeds, matrices, version information, and hashes under ignored results/. Retain extinction runs, distinguish stochastic variability from parameter uncertainty, and flag unresolved outcomes at finite horizons.
