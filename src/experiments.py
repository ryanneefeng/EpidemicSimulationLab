"""Compare hypothetical disease settings across repeated random seeds."""

import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import statistics

from src.simulation import simulate


ROOT = Path(__file__).resolve().parents[1]


def summarize_runs(rows):
    if len(rows) < 2:
        raise ValueError("Use at least two replicates to estimate variation.")
    result = {"replicates": len(rows)}
    for name, values in (
        ("attack_percent", [100 * row["attack_fraction"] for row in rows]),
        ("deaths", [row["deaths"] for row in rows]),
    ):
        result[f"{name}_mean"] = statistics.mean(values)
        result[f"{name}_sd"] = statistics.stdev(values)
        result[f"{name}_mcse"] = statistics.stdev(values) / math.sqrt(len(values))
    result["no_secondary_fraction"] = sum(row["secondary_infections"] == 0 for row in rows) / len(rows)
    result["unresolved_runs"] = sum(row["unresolved"] > 0 for row in rows)
    return result


def run_study(scenario, matrix, replicates=20):
    if type(replicates) is not int or replicates < 2:
        raise ValueError("Use at least two whole-number replicates.")
    rows, summaries = [], []
    for transmission in (0.04, 0.20):
        for mortality in (0.05, 0.50):
            cell = []
            for seed in range(replicates):
                settings = {
                    **scenario, "random_seed": seed,
                    "transmission_probability_per_active_encounter": transmission,
                    "death_probability_per_infection": mortality,
                }
                result = simulate(settings, matrix)
                cell.append({"transmission": transmission, "mortality": mortality,
                             "seed": seed, **result["metrics"]})
            rows.extend(cell)
            summaries.append({"transmission": transmission, "mortality": mortality, **summarize_runs(cell)})
    return {
        "base_scenario": scenario, "contact_matrix": matrix,
        "seed_range_inclusive": [0, replicates - 1],
        "design": "Paired seeds across four cells; all runs retained, including early extinction.",
        "rows": rows, "summary": summaries,
    }


def save_study(result, directory):
    """Save generated results and the inputs needed to reproduce them."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "replicates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["rows"][0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(result["rows"])
    inputs = ["model.py", "src/model.py", "src/simulation.py", "src/country_data.py",
              "src/experiments.py", "scenarios/example.json", "data/demographics.csv",
              "data/contacts.csv", "data/SOURCES.json"]
    report = {
        **{key: value for key, value in result.items() if key != "rows"},
        "python_version": platform.python_version(),
        "input_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs},
        "replicates_sha256": hashlib.sha256((directory / "replicates.csv").read_bytes()).hexdigest(),
    }
    (directory / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def print_study(result):
    print("\nAttack = percentage ever infected, including initial cases.")
    print("SD describes differences between runs; MCSE describes uncertainty in the estimated mean.")
    print("\n p(%)  f(%)   Attack mean / SD / MCSE (%)   Deaths mean / SD / MCSE   No spread   Unresolved")
    for cell in result["summary"]:
        attack = " / ".join(f"{cell['attack_percent_' + key]:.2f}" for key in ("mean", "sd", "mcse"))
        deaths = " / ".join(f"{cell['deaths_' + key]:.2f}" for key in ("mean", "sd", "mcse"))
        print(f"{100 * cell['transmission']:5.0f} {100 * cell['mortality']:5.0f}"
              f" {attack:>30} {deaths:>27} {cell['no_secondary_fraction']:>10.0%}"
              f" {cell['unresolved_runs']:>12}")
