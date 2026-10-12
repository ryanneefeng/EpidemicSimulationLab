# Data sources and import requirements

Country/city data are a core part of this project. Build a reproducible import pipeline early, starting with one country and one city/locality demographic file.

## Contact data candidate checked on October 12, 2026

https://github.com/kieshaprem/synthetic-contact-matrices

The repository describes synthetic matrices for 177 geographical locations and rural/urban customization. Its `output/syntheticmatrices` directory contains R `.rdata` files for all, home, school, work, and other contacts, plus rural and urban folders. These are projected matrices, not measured contact networks for every city. No files have been downloaded or imported yet. Importing R-format outputs will require a suitable reader or a documented conversion; do not assume these are country CSV files.

First inspect an actual file and its generation documentation: country names/codes, dimensions, age labels including the oldest bin, orientation, daily-contact definition, survey/demographic period, setting, and version. Record the repository commit or release, source URL, date retrieved, original filename, checksum, transformations, and applicable attribution/license information.

## Demographics

Use an official census/statistical source where available. Store age-bin counts, geographic identifier, reference year, units, and source. Retain original counts separately from a smaller synthetic population. Do not turn an unsupported country contact matrix into city-specific evidence silently; show the selected geographic proxy and demographic adjustment.

## Consistent age groups

Keep source data at its original resolution. Aggregate participant rows with population weights and sum contact columns; declare C[i,j] as daily contacts an age-i participant has with age-j people. For shared undirected contacts require N[i]C[i,j] = N[j]C[j,i], documenting balancing.

Editable groups do not create information absent from data. Boundaries aligned with source bins can be aggregated. Splitting a source bin requires additional data or an explicit interpolation assumption. A terminal 75+ or 80+ bin cannot be subdivided without added evidence. Data used to weight aggregation must have compatible age coverage.

## Contact networks

Average contact matrices do not identify unique partners, relationship duration, or encounter recurrence. These require additional data or documented assumptions and sensitivity analysis. Household/school/work/other layers should share a total contact budget; do not add setting-specific matrices to the already-total matrix and double count contacts.
