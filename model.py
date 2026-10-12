"""Choose country and disease settings in the terminal."""

import argparse
import json
from pathlib import Path

from src.country_data import country_scenario, load_countries
from src.model import age_labels, create_population, summarize_population, validate_scenario


ROOT = Path(__file__).resolve().parent


def choose_country(countries, value):
    key = value.strip().casefold()
    matches = [country for code, country in countries.items() if key in (code.casefold(), country["name"].casefold())]
    if len(matches) != 1:
        raise ValueError("Enter a country code or full name from --list-countries.")
    return matches[0]


def ask_country(countries, default):
    while True:
        value = input(f"Country code or name [{default}]: ").strip() or default
        try:
            return choose_country(countries, value)
        except ValueError as error:
            print(error)


def ask_number(label, default, minimum, maximum, whole=True, allowed=None):
    while True:
        text = input(f"{label} [{default}]: ").strip()
        try:
            value = default if not text else (int(text) if whole else float(text))
            if not minimum <= value <= maximum or (allowed is not None and value not in allowed):
                raise ValueError
            return value
        except ValueError:
            options = f"Choose one of {', '.join(map(str, allowed))}." if allowed else f"Enter a number from {minimum} to {maximum}."
            print(options)


def show_results(country, scenario, population, matrix):
    people = create_population(scenario)
    summary = summarize_population(people, scenario)
    labels = age_labels(scenario["age_lower_bounds_years"])
    print(f"\nCountry: {country['name']} ({country['code']})")
    print(f"Demographics: UN WPP 2019 revision, 1 July {country['year']}; both sexes.")
    print(f"Country population: {sum(population):,}; simulated people: {len(people):,}.")
    print(f"Transmission: {scenario['transmission_probability_per_active_encounter'] * 100:g}% per encounter.")
    print(f"Mortality: {scenario['death_probability_per_infection'] * 100:g}% per infection. Seed: {scenario['random_seed']}.")
    print("\nAge group     Country people    Share   Simulated   Infectious")
    for label, count, group in zip(labels, population, summary["age_groups"]):
        share = count / sum(population) * 100
        print(f"{label:<12} {count:>14,} {share:>7.2f}% {group['population']:>10} {group['I']:>12}")
    print("\nDay 0: " + ", ".join(f"{name}={count}" for name, count in summary["states"].items()))
    print("S=susceptible, E=exposed, I=infectious, R=recovered, D=dead.")
    print("Everyone starts unvaccinated. No disease events have advanced yet.")
    print("\nSynthetic daily contacts (Prem et al., 2021; overall, all locations)")
    print("Rows: participant age. Columns: age of the people contacted.")
    print(f"{'Age':<8}" + "".join(f"{label:>8}" for label in labels))
    for label, row in zip(labels, matrix):
        print(f"{label:<8}" + "".join(f"{value:>8.2f}" for value in row))
    print("These contact averages are inputs for a later spread model.")
    print("\nFinished. You can change the settings and run again.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", action="store_true", help="Print results with saved defaults; no questions.")
    parser.add_argument("--country", help="Country code or full name to use as the default.")
    parser.add_argument("--list-countries", action="store_true", help="List countries with both datasets, then exit.")
    args = parser.parse_args()
    print("Epidemic Scenario Lab - terminal setup", flush=True)
    try:
        countries = load_countries()
        if args.list_countries:
            for country in sorted(countries.values(), key=lambda country: country["name"]):
                print(f"{country['code']}  {country['name']}")
            print(f"\n{len(countries)} countries/areas with demographics and contact matrices.")
            return
        settings = json.loads((ROOT / "scenarios/example.json").read_text(encoding="utf-8"))
        if args.country:
            settings["country"] = choose_country(countries, args.country)["code"]
        if args.example:
            country = choose_country(countries, settings["country"])
        else:
            print("Press Enter to keep a default. Age-group counts come from country data.", flush=True)
            country = ask_country(countries, settings["country"])
            settings["simulation_population"] = ask_number("Simulated people", settings["simulation_population"], 1, 10000)
            settings["age_group_width"] = ask_number("Age-group width (5, 10, or 20 years)", settings["age_group_width"], 5, 20, allowed=(5, 10, 20))
            settings["initial_infectious"] = ask_number("Initially infectious", settings["initial_infectious"], 0, settings["simulation_population"])
            for label, key in (("Transmission (%)", "transmission_probability_per_active_encounter"), ("Mortality (%)", "death_probability_per_infection")):
                settings[key] = ask_number(label, settings[key] * 100, 0, 100, whole=False) / 100
            settings["random_seed"] = ask_number("Random seed", settings["random_seed"], 0, 2147483647)
        settings["name"] = f"{country['name']} scenario"
        scenario, population, matrix = country_scenario(country, settings)
        show_results(country, validate_scenario(scenario), population, matrix)
    except EOFError:
        parser.exit(1, "Input unavailable. Use VS Code's Terminal, or run python model.py --example.\n")
    except KeyboardInterrupt:
        print("\nCancelled.")
    except FileNotFoundError as error:
        parser.exit(1, f"Missing file: {error.filename}. Run python prepare_data.py to restore the country data.\n")
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Could not create the population: {error}\n")


if __name__ == "__main__":
    main()
