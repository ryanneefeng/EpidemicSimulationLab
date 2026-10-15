# Data sources and transformations

Sources inspected October 12, 2026. The prepared CSV files are committed so terminal runs work offline without additional packages.

## Demographics

Source: United Nations, Department of Economic and Social Affairs, Population Division (2019), *World Population Prospects 2019*, Online Edition, Rev. 1. The research repository's `popage_total2020.csv` contains both-sex population projections for 1 July 2020, in thousands, for 201 countries/areas. Its upstream processing code multiplies values by 1000; our importer does the same using exact decimal arithmetic.

[Original file](https://github.com/kieshaprem/synthetic-contact-matrices/blob/7fcb6985dbc3070cdcb3e5daa5f6b26ce2605d69/generate_synthetic_matrices/input/pop/popage_total2020.csv) and [source processing code](https://github.com/kieshaprem/synthetic-contact-matrices/blob/7fcb6985dbc3070cdcb3e5daa5f6b26ce2605d69/generate_synthetic_matrices/codes/pop_getPopAge.r).

`data/demographics.csv` has one row per location: country code/name, year, age_0_4 through age_95_99, age_100_plus, and population_total. Values are people. Source counts are retained separately from the simulation population. Newer estimates are available through [UN World Population Prospects](https://population.un.org/wpp/); importing a newer revision is a separate data update.

Country names join to ISO3 codes through the countrycode dictionary, pinned at commit `9546912ab023a6445cbe7b5620f5103446d84e52`. Eight spelling/name variants use explicit aliases recorded in `data/SOURCES.json`. Channel Islands is an aggregate without one ISO3 code: its demographic row remains with a blank code and cannot be selected as a contact preset.

## Contacts

Source: Kiesha Prem and collaborators (2021), *Projecting contact matrices in 177 geographical regions: an update and comparison with empirical data for the COVID-19 era*, [paper](https://doi.org/10.1371/journal.pcbi.1009098) and [repository](https://github.com/kieshaprem/synthetic-contact-matrices).

The repository also contains a CSV at `generate_synthetic_matrices/output/syntheticmatrices/synthetic_contacts_2021.csv`. Its export labels the oldest group **75+**, but the [2024 correction](https://doi.org/10.1371/journal.pcbi.1012454) clarifies that source coverage stops at age 80. Treat that source bin as 75-79. This CSV can be imported without an R reader.

`data/contacts.csv` keeps overall geography and all contact locations: 177 complete 16 by 16 matrices, stored as one row per country and age pair. Columns are country_code, participant_age_lower, contact_age_lower, and mean_daily_contacts. Bounds are 0, 5, ..., 75; the final bound means 75+. The importer explicitly handles the upstream spelling `age_cotactee`.

C[i,j] means average daily contacts an age-i participant has with age-j people. These are synthetic country estimates. The ignored original download also preserves home, work, school, other, urban, and rural variants for later work. Avoid adding the already-total matrix to its setting-specific parts.

## Combine compatible ages

Ryan's approved approximation (Day 2): use the source's final 75-79 row and column unchanged for a single **75+** group. Sum demographic ages 75-79 through 100+ into that group. Do not duplicate the contact column or multiply its rates by the added population. These are assumed rates for 75+, not measured rates for ages 80+.

Then group both datasets at width 5, 10, or 20. The oldest modeled group is respectively 75+, 70+, or 60+; the latter two include the approximated 75+ bin. This imported matrix cannot support a separate contact boundary at 80. Age aggregation preserves contact volume under the extended population weights, not an observed contact total for older adults.

Population counts add across source bins. Contact columns add; participant rows use country population weights. For new groups A and B:

`C_new[A,B] = sum(N[i] * sum(C[i,j] for j in B) for i in A) / sum(N[i] for i in A)`

This preserves total expected contacts weighted over the population. It does not force symmetry. Before generating undirected relationships, check and document balancing so N[i]C[i,j] = N[j]C[j,i].

For a small simulation, allocate people in proportion to the country age distribution. Round down first, then assign remaining people to the largest fractional remainders, breaking ties by age order. The counts always sum to the requested size. Tiny age groups may round to zero; no minimum count is invented.

## Reproduce and extend

`prepare_data.py` pins the Prem repository at `7fcb6985dbc3070cdcb3e5daa5f6b26ce2605d69`, verifies downloaded SHA-256 checksums, converts counts, validates complete matrices, and records output checksums in `data/SOURCES.json`. Raw downloads are kept locally under ignored `data/raw/`; prepared data and attribution stay in Git. Imported data carries the upstream GPL-3.0 notice in `data/LICENSE`; project Python code has its own root license.

The terminal is a population initialization exercise. Contact averages do not specify unique partners or repeated relationships. Locality data, modern demographic revisions, network assumptions, disease durations, and vaccine policies require later work with explicit sources and validation.
