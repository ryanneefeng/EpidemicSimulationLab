"""Prepare country demographics and contact CSV files."""

import argparse
import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import shutil
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RAW = DATA / "raw"
PREM_COMMIT = "7fcb6985dbc3070cdcb3e5daa5f6b26ce2605d69"
CODE_COMMIT = "9546912ab023a6445cbe7b5620f5103446d84e52"
PREM_URL = f"https://raw.githubusercontent.com/kieshaprem/synthetic-contact-matrices/{PREM_COMMIT}"
CODE_URL = f"https://raw.githubusercontent.com/vincentarelbundock/countrycode/{CODE_COMMIT}"
SOURCES = {
    "popage_total2020.csv": {
        "url": f"{PREM_URL}/generate_synthetic_matrices/input/pop/popage_total2020.csv",
        "sha256": "4847f6e62f462ffa41bb8c80107688070082a761f6f2f510fa26efd4046aad00",
    },
    "synthetic_contacts_2021.csv": {
        "url": f"{PREM_URL}/generate_synthetic_matrices/output/syntheticmatrices/synthetic_contacts_2021.csv",
        "sha256": "aefe4f0618e6e38e57fe79d08377fa7d35e02489ba90203025308afd82387d32",
    },
    "country_codes.csv": {
        "url": f"{CODE_URL}/dictionary/codelist_without_cldr.csv",
        "sha256": "e7b7da2fc7d0195c72bac7ebed102ce391d4e31618595c68ad2f22a43bbfbde7",
    },
    "LICENSE-source.txt": {
        "url": f"{PREM_URL}/LICENSE",
        "sha256": "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986",
    },
}
ALIASES = {
    "State of Palestine": "PSE",
    "China, Hong Kong SAR": "HKG",
    "China, Macao SAR": "MAC",
    "China, Taiwan Province of China": "TWN",
    "Dem. People's Republic of Korea": "PRK",
    "Lao People's Democratic Republic": "LAO",
    "United States Virgin Islands": "VIR",
    "Micronesia (Fed. States of)": "FSM",
    "Channel Islands": "",
}
AGE_COLUMNS = [f"age_{age}_{age + 4}" for age in range(0, 100, 5)] + ["age_100_plus"]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def fetch_sources(offline):
    RAW.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        path = RAW / name
        if not path.exists():
            if offline:
                raise ValueError(f"Missing {name}. Run without --offline to download it.")
            print(f"Downloading {name}...", flush=True)
            with urlopen(source["url"], timeout=60) as response, path.open("wb") as handle:
                shutil.copyfileobj(response, handle)
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Checksum failed for {name}. Remove that raw file and download it again.")


def demographics():
    dictionary = read_csv(RAW / "country_codes.csv")
    rows = []
    used_codes = set()
    for source in read_csv(RAW / "popage_total2020.csv"):
        name = source["Region, subregion, country or area *"]
        if name in ALIASES:
            code = ALIASES[name]
        else:
            matches = {
                row["iso3c"] for row in dictionary
                if row["iso3c"] and any(
                    value.casefold() == name.casefold()
                    for key, value in row.items() if ".name." in key and "regex" not in key
                )
            }
            if len(matches) != 1:
                raise ValueError(f"Country name needs review: {name}")
            code = matches.pop()
        if code and code in used_codes:
            raise ValueError(f"Duplicate country code: {code}")
        used_codes.add(code)
        counts = []
        for age in range(0, 101, 5):
            count = Decimal(source[f"age{age}"]) * 1000
            if not count.is_finite() or count < 0 or count != count.to_integral_value():
                raise ValueError(f"Invalid population count: {name}, age {age}")
            counts.append(int(count))
        rows.append({
            "country_code": code, "country": name,
            "year": int(source["Reference date (as of 1 July)"]),
            **dict(zip(AGE_COLUMNS, counts)), "population_total": sum(counts),
        })
    return sorted(rows, key=lambda row: row["country"])


def contacts():
    rows = []
    cells = set()
    with (RAW / "synthetic_contacts_2021.csv").open(encoding="utf-8-sig", newline="") as handle:
        for source in csv.DictReader(handle):
            if source["setting"] != "overall" or source["location_contact"] != "all":
                continue
            code = source["iso3c"]
            participant = int(source["age_contactor"].split()[0].rstrip("+"))
            contact = int(source["age_cotactee"].split()[0].rstrip("+"))
            value = float(source["mean_number_of_contacts"])
            cell = (code, participant, contact)
            if cell in cells or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid or duplicate contact cell: {cell}")
            if participant not in range(0, 76, 5) or contact not in range(0, 76, 5):
                raise ValueError(f"Unexpected contact age: {cell}")
            cells.add(cell)
            rows.append({
                "country_code": code, "participant_age_lower": participant,
                "contact_age_lower": contact, "mean_daily_contacts": value,
            })
    countries = {row["country_code"] for row in rows}
    if len(countries) != 177 or len(rows) != 177 * 16 * 16:
        raise ValueError("Expected 177 complete 16 by 16 contact matrices.")
    return sorted(rows, key=lambda row: (row["country_code"], row["participant_age_lower"], row["contact_age_lower"]))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Use verified raw files already downloaded.")
    args = parser.parse_args()
    try:
        fetch_sources(args.offline)
        population_rows = demographics()
        contact_rows = contacts()
        population_codes = {row["country_code"] for row in population_rows}
        contact_codes = {row["country_code"] for row in contact_rows}
        if not contact_codes <= population_codes:
            raise ValueError(f"Missing demographics for {sorted(contact_codes - population_codes)}")
        write_csv(DATA / "demographics.csv", population_rows)
        write_csv(DATA / "contacts.csv", contact_rows)
        shutil.copyfile(RAW / "LICENSE-source.txt", DATA / "LICENSE")
        metadata = {
            "sources_checked_on": "2026-10-12", "sources": SOURCES,
            "demographics": "UN World Population Prospects 2019, Rev. 1; both sexes, 1 July 2020.",
            "population_conversion": "Source thousands multiplied by 1000; native five-year groups through 100+ retained.",
            "contacts": "Prem et al. (2021), synthetic; overall setting, all contact locations; five-year groups ending in 75+.",
            "orientation": "C[i,j] = mean daily contacts an age-i participant has with age-j people.",
            "country_name_aliases": ALIASES,
            "unmatched_iso_note": "Channel Islands is an aggregate without a single ISO3 code; retained with blank code.",
            "demographic_locations": len(population_rows), "contact_locations": len(contact_codes),
            "repository_licenses": "Both source repositories use GPL-3.0; see data/LICENSE. Credit underlying UN data separately.",
            "outputs_sha256": {
                name: hashlib.sha256((DATA / name).read_bytes()).hexdigest()
                for name in ("demographics.csv", "contacts.csv")
            },
        }
        (DATA / "SOURCES.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        print(f"Ready: {len(population_rows)} demographic locations and {len(contact_codes)} contact matrices.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Data preparation failed: {error}\n")


if __name__ == "__main__":
    main()
