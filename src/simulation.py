"""Advance a daily, stochastic SEIRD model."""

from src.model import DiseaseState as State


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
