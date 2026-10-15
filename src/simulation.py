"""Advance a daily, stochastic SEIRD model."""

import math

from src.model import DiseaseState as State


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
