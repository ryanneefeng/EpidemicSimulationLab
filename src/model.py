"""Create the starting population from user-chosen settings."""

from dataclasses import asdict, dataclass
from enum import Enum
import math
import random


class DiseaseState(str, Enum):
    SUSCEPTIBLE = "S"
    EXPOSED = "E"
    INFECTIOUS = "I"
    RECOVERED = "R"
    DEAD = "D"


@dataclass
class Person:
    identifier: int
    age_group: str
    state: DiseaseState = DiseaseState.SUSCEPTIBLE
    vaccinated: bool = False
    days_in_state: int = 0


def validate_scenario(scenario):
    if not isinstance(scenario, dict):
        raise ValueError("Settings must be a JSON object.")
    name = scenario.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Enter a scenario name.")
    population = scenario.get("simulation_population")
    if type(population) is not int or not 1 <= population <= 10000:
        raise ValueError("Population must be a whole number from 1 to 10,000.")
    bounds = scenario.get("age_lower_bounds_years")
    if not isinstance(bounds, list) or not bounds:
        raise ValueError("Enter age lower bounds, starting with 0.")
    if any(type(age) is not int or age < 0 for age in bounds):
        raise ValueError("Age lower bounds must be nonnegative whole numbers.")
    if bounds[0] != 0 or bounds != sorted(set(bounds)):
        raise ValueError("Age lower bounds must start at 0 and increase strictly.")
    counts = scenario.get("age_group_counts")
    if not isinstance(counts, list) or len(counts) != len(bounds):
        raise ValueError("Enter one population count for each age group.")
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("Age-group counts must be nonnegative whole numbers.")
    if sum(counts) != population:
        raise ValueError("Age-group counts must add up to the population.")
    for key in ("transmission_probability_per_active_encounter", "death_probability_per_infection"):
        value = scenario.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError("Transmission and mortality must be between 0% and 100%.")
    infectious = scenario.get("initial_infectious")
    if type(infectious) is not int or not 0 <= infectious <= population:
        raise ValueError("Initially infectious people must be between 0 and the population.")
    seed = scenario.get("random_seed")
    if type(seed) is not int or seed < 0:
        raise ValueError("The random seed must be a nonnegative whole number.")
    for key in ("latent_days", "infectious_days", "simulation_days"):
        value = scenario.get(key)
        if type(value) is not int or not 1 <= value <= 3650:
            raise ValueError(f"{key} must be a whole number from 1 to 3650.")
    return {**scenario, "name": name.strip()}


def age_labels(bounds):
    labels = [f"{low}-{high - 1}" for low, high in zip(bounds, bounds[1:])]
    return labels + [f"{bounds[-1]}+"]


def create_population(scenario):
    scenario = validate_scenario(scenario)
    people = []
    for label, count in zip(age_labels(scenario["age_lower_bounds_years"]), scenario["age_group_counts"]):
        for _ in range(count):
            people.append(Person(len(people) + 1, label))
    rng = random.Random(scenario["random_seed"])
    for person in rng.sample(people, scenario["initial_infectious"]):
        person.state = DiseaseState.INFECTIOUS
    return people


def summarize_population(people, scenario):
    totals = {state.value: 0 for state in DiseaseState}
    groups = {label: {**totals} for label in age_labels(scenario["age_lower_bounds_years"])}
    for person in people:
        totals[person.state.value] += 1
        groups[person.age_group][person.state.value] += 1
    infectious = [person for person in people if person.state == DiseaseState.INFECTIOUS]
    susceptible = [person for person in people if person.state == DiseaseState.SUSCEPTIBLE]
    sample = infectious[:4] + susceptible[:8 - min(4, len(infectious))]
    return {
        "population": len(people),
        "states": totals,
        "age_groups": [{"label": label, "population": sum(counts.values()), **counts} for label, counts in groups.items()],
        "sample": [asdict(person) for person in sample],
    }
