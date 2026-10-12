"""Read editable scenario settings. This does not simulate an epidemic yet."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario", nargs="?", type=Path,
        default=Path(__file__).parent / "scenarios" / "example.json",
    )
    args = parser.parse_args()
    scenario = json.loads(args.scenario.read_text(encoding="utf-8"))

    probability_names = [
        "transmission_probability_per_active_encounter",
        "death_probability_per_infection",
    ]
    for name in probability_names:
        value = scenario[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be a number between 0 and 1.")

    bounds = scenario["age_lower_bounds_years"]
    if not bounds or any(type(age) is not int or age < 0 for age in bounds):
        raise ValueError("Age lower bounds must be nonnegative integers.")
    if bounds[0] != 0 or bounds != sorted(set(bounds)):
        raise ValueError("Age lower bounds must start at 0 and increase strictly.")
    population = scenario["simulation_population"]
    if type(population) is not int or population <= 0:
        raise ValueError("Simulation population must be a positive integer.")

    groups = [f"{low}-{high - 1}" for low, high in zip(bounds, bounds[1:])]
    groups.append(f"{bounds[-1]}+")
    print(f"Scenario: {scenario['name']}")
    print("Loaded settings. No epidemic has been simulated yet.")
    print(f"Planned population: {population} people")
    print("Age groups: " + ", ".join(groups))
    print(f"Transmission per active encounter: {scenario[probability_names[0]] * 100:g}%")
    print("  Applies when an infectious person encounters a susceptible person.")
    print(f"Death probability per infection: {scenario[probability_names[1]] * 100:g}%")
    print("  Applies to people who become infected, not the whole population.")
    print("These probabilities describe chances, not guaranteed counts.")
    print("Next: create people and track their disease states.")


if __name__ == "__main__":
    main()
