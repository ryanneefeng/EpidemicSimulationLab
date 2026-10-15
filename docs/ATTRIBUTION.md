# Attribution

Related prior work: *Simulation of Vaccine Deployment for a Hypothetical Omega Variant in Tompkins County, NY* (October 8, 2026), by Ryan Feng, Sophia Doyle, and Thomas Fiske.

The paper credits joint initial planning, Ryan's research and parameter interpretation, Sophia's report writing and LaTeX organization, and Thomas's modeling, MATLAB implementation, and stress testing. Preserve these contributions. The paper serves as reference; its parameters, age groups, optimization weights, and model structure are not requirements for this project.

The majority of this project's codebase was built through Ryan Feng's work with OpenAI Codex. Ryan independently conceived and approved the mathematical backbone, research-data selection, and modeling direction. Codex contributed implementation, debugging, tests, derivations, and documentation under his direction. This disclosure does not transfer credit for the underlying research datasets or the earlier team's work.

New implementation-level assumptions proposed by Codex on Day 2 (daily Poisson exposure opportunities, fixed stage durations, and mortality timing) are provisional working choices for Ryan to review. The 75+ contact approximation was explicitly approved by Ryan. Git history records implementation milestones; it does not by itself establish human approval of each new scientific assumption.

Contact data: Kiesha Prem and collaborators, *Projecting contact matrices in 177 geographical regions: an update and comparison with empirical data for the COVID-19 era* (2021), [paper](https://doi.org/10.1371/journal.pcbi.1009098), [source repository](https://github.com/kieshaprem/synthetic-contact-matrices).

Demographic data: United Nations, Department of Economic and Social Affairs, Population Division (2019), *World Population Prospects 2019*, Online Edition, Rev. 1; both-sex 2020 age populations, distributed in the Prem research repository.

Country-name matching: [countrycode project and contributors](https://github.com/vincentarelbundock/countrycode). Source commits, checksums, explicit name mappings, and transformations are recorded in data/SOURCES.json and docs/DATA_SOURCES.md. Upstream GPL-3.0 license text is retained in data/LICENSE.
