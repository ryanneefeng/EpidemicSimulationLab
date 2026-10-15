"""Load country data and combine compatible age groups."""

import csv
import math
from pathlib import Path


DATA = Path(__file__).resolve().parents[1] / "data"
SOURCE_BOUNDS = list(range(0, 76, 5))
AGE_COLUMNS = [f"age_{age}_{age + 4}" for age in range(0, 100, 5)] + ["age_100_plus"]


def load_countries():
    countries = {}
    with (DATA / "demographics.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if not row["country_code"]:
                continue
            counts = [int(row[column]) for column in AGE_COLUMNS]
            if any(count < 0 for count in counts) or sum(counts) != int(row["population_total"]):
                raise ValueError(f"Invalid demographics for {row['country']}")
            if row["country_code"] in countries:
                raise ValueError("Duplicate demographic country code.")
            # Use the final source contact bin for everyone aged 75+.
            countries[row["country_code"]] = {
                "code": row["country_code"], "name": row["country"], "year": int(row["year"]),
                "population": counts[:15] + [sum(counts[15:])],
                "contacts": [[None] * 16 for _ in SOURCE_BOUNDS],
            }
    with (DATA / "contacts.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            country = countries[row["country_code"]]
            i = SOURCE_BOUNDS.index(int(row["participant_age_lower"]))
            j = SOURCE_BOUNDS.index(int(row["contact_age_lower"]))
            if country["contacts"][i][j] is not None:
                raise ValueError("Duplicate contact cell.")
            value = float(row["mean_daily_contacts"])
            if not math.isfinite(value) or value < 0:
                raise ValueError("Contact averages must be finite and nonnegative.")
            country["contacts"][i][j] = value
    for country in countries.values():
        cells = [value for row in country["contacts"] for value in row]
        if any(value is not None for value in cells) and any(value is None for value in cells):
            raise ValueError(f"Incomplete contact matrix for {country['name']}")
    return {
        code: country for code, country in countries.items()
        if all(value is not None for row in country["contacts"] for value in row)
    }


def aggregate_contacts(matrix, population, groups):
    result = []
    for participant_group in groups:
        total = sum(population[i] for i in participant_group)
        if total <= 0:
            raise ValueError("Cannot weight a group with no population.")
        result.append([
            sum(population[i] * sum(matrix[i][j] for j in contact_group) for i in participant_group) / total
            for contact_group in groups
        ])
    return result


def allocate_people(population, size):
    total = sum(population)
    if total <= 0 or type(size) is not int or size < 1:
        raise ValueError("Choose a positive simulation size and population.")
    counts = [size * count // total for count in population]
    order = sorted(range(len(population)), key=lambda i: (-(size * population[i] % total), i))
    for i in order[:size - sum(counts)]:
        counts[i] += 1
    return counts


def country_scenario(country, settings):
    width = settings["age_group_width"]
    if type(width) is not int or width not in (5, 10, 20):
        raise ValueError("Age-group width must be 5, 10, or 20 years.")
    bounds = list(range(0, 76, width))
    groups = [
        [i for i, age in enumerate(SOURCE_BOUNDS) if low <= age < high]
        for low, high in zip(bounds, bounds[1:] + [101])
    ]
    population = [sum(country["population"][i] for i in group) for group in groups]
    scenario = {
        **settings, "country": country["code"], "country_name": country["name"],
        "demographic_year": country["year"], "age_lower_bounds_years": bounds,
        "age_group_counts": allocate_people(population, settings["simulation_population"]),
    }
    return scenario, population, aggregate_contacts(country["contacts"], country["population"], groups)
