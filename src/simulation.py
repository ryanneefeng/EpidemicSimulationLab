"""Advance a daily, stochastic SEIRD model."""

import math
import random

from src.model import DiseaseState as State
from src.model import age_labels, create_population, validate_scenario


def validate_contacts(matrix, size):
    if len(matrix) != size or any(len(row) != size for row in matrix):
        raise ValueError("Contact matrix must match the scenario's age groups.")
    if any(type(value) not in (int, float) or not math.isfinite(value) or value < 0
           for row in matrix for value in row):
        raise ValueError("Contact rates must be finite and nonnegative.")


def infection_probabilities(matrix, counts, susceptible, infectious, probability):
    """Daily risks under Poisson exposure opportunities; exclude oneself."""
    risks = []
    for i, row in enumerate(matrix):
        if susceptible[i] == 0:
            risks.append(0.0)
            continue
        infectious_contacts = 0.0
        for j, rate in enumerate(row):
            pool = counts[j] - (i == j)
            if pool > 0:
                infectious_contacts += rate * (infectious[j] / pool)
        risks.append(-math.expm1(-probability * infectious_contacts) if probability else 0.0)
    return risks


def advance_disease(people, scenario, exposed_ids, outcome_rng):
    """Apply exposures and progress existing stages at the day's boundary."""
    susceptible_ids = {p.identifier for p in people if p.state == State.SUSCEPTIBLE}
    if not set(exposed_ids) <= susceptible_ids:
        raise ValueError("New exposures must refer to susceptible people.")
    flows = {"new_exposures": 0, "new_infectious": 0, "new_recoveries": 0, "new_deaths": 0}
    for person in people:
        if person.state == State.SUSCEPTIBLE and person.identifier in exposed_ids:
            person.state = State.EXPOSED
            person.days_in_state = 0
            flows["new_exposures"] += 1
        elif person.state == State.EXPOSED:
            person.days_in_state += 1
            if person.days_in_state >= scenario["latent_days"]:
                person.state = State.INFECTIOUS
                person.days_in_state = 0
                flows["new_infectious"] += 1
        elif person.state == State.INFECTIOUS:
            person.days_in_state += 1
            if person.days_in_state >= scenario["infectious_days"]:
                dies = outcome_rng.random() < scenario["death_probability_per_infection"]
                person.state = State.DEAD if dies else State.RECOVERED
                person.days_in_state = 0
                flows["new_deaths" if dies else "new_recoveries"] += 1
    return flows


def simulate(scenario, matrix):
    """Run until the horizon or until no exposed/infectious people remain."""
    scenario = validate_scenario(scenario)
    labels = age_labels(scenario["age_lower_bounds_years"])
    validate_contacts(matrix, len(labels))
    counts = scenario["age_group_counts"]
    people = create_population(scenario)
    group_index = {label: i for i, label in enumerate(labels)}
    transmission_rng = random.Random(f"transmission:{scenario['random_seed']}")
    outcome_rng = random.Random(f"outcome:{scenario['random_seed']}")

    def snapshot(day, flows):
        states = {state.value: 0 for state in State}
        for person in people:
            states[person.state.value] += 1
        return {"day": day, **states, **flows, "cumulative_infections": len(people) - states["S"]}

    history = [snapshot(0, {"new_exposures": 0, "new_infectious": 0, "new_recoveries": 0, "new_deaths": 0})]
    for day in range(1, scenario["simulation_days"] + 1):
        if history[-1]["E"] + history[-1]["I"] == 0:
            break
        susceptible = [0] * len(labels)
        infectious = [0] * len(labels)
        for person in people:
            index = group_index[person.age_group]
            susceptible[index] += person.state == State.SUSCEPTIBLE
            infectious[index] += person.state == State.INFECTIOUS
        risks = infection_probabilities(matrix, counts, susceptible, infectious,
                                        scenario["transmission_probability_per_active_encounter"])
        exposed_ids = {
            person.identifier for person in people
            if person.state == State.SUSCEPTIBLE
            and transmission_rng.random() < risks[group_index[person.age_group]]
        }
        flows = advance_disease(people, scenario, exposed_ids, outcome_rng)
        history.append(snapshot(day, flows))

    final = history[-1]
    peak = max(history, key=lambda row: row["I"])
    unresolved = final["E"] + final["I"]
    metrics = {
        "end_day": final["day"], "total_infections": final["cumulative_infections"],
        "secondary_infections": final["cumulative_infections"] - scenario["initial_infectious"],
        "attack_fraction": final["cumulative_infections"] / len(people),
        "deaths": final["D"], "peak_infectious": peak["I"], "peak_day": peak["day"],
        "unresolved": unresolved, "extinction_day": None if unresolved else final["day"],
    }
    return {"history": history, "metrics": metrics}
