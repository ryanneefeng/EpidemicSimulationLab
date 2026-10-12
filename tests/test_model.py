"""Check population accounting and reproducible starting states."""

from dataclasses import asdict
import json
from pathlib import Path
import random
import unittest

from src.model import create_population, summarize_population, validate_scenario


class PopulationTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "scenarios/example.json"
        self.scenario = json.loads(path.read_text(encoding="utf-8"))

    def test_population_and_age_accounting(self):
        people = create_population(self.scenario)
        summary = summarize_population(people, self.scenario)
        self.assertEqual(sum(summary["states"].values()), len(people))
        self.assertEqual(len(people), self.scenario["simulation_population"])
        self.assertEqual(summary["states"]["I"], self.scenario["initial_infectious"])
        self.assertEqual([group["population"] for group in summary["age_groups"]], self.scenario["age_group_counts"])
        self.assertEqual(len({person.identifier for person in people}), len(people))
        self.assertTrue(all(not person.vaccinated for person in people))

    def test_custom_age_groups(self):
        scenario = {**self.scenario, "simulation_population": 20, "age_lower_bounds_years": [0, 18, 65], "age_group_counts": [5, 10, 5], "initial_infectious": 3}
        summary = summarize_population(create_population(scenario), scenario)
        self.assertEqual(summary["states"], {"S": 17, "E": 0, "I": 3, "R": 0, "D": 0})
        self.assertEqual([group["label"] for group in summary["age_groups"]], ["0-17", "18-64", "65+"])

    def test_seed_repeats_starting_people(self):
        first = [asdict(person) for person in create_population(self.scenario)]
        second = [asdict(person) for person in create_population(self.scenario)]
        self.assertEqual(first, second)

    def test_population_randomness_is_independent(self):
        previous = random.getstate()
        create_population(self.scenario)
        self.assertEqual(random.getstate(), previous)

    def test_infectious_boundaries(self):
        for count in (0, self.scenario["simulation_population"]):
            with self.subTest(infectious=count):
                scenario = {**self.scenario, "initial_infectious": count}
                summary = summarize_population(create_population(scenario), scenario)
                self.assertEqual(summary["states"]["I"], count)
                self.assertEqual(summary["states"]["S"], scenario["simulation_population"] - count)

    def test_probabilities_do_not_create_day_zero_outcomes(self):
        scenario = {**self.scenario, "transmission_probability_per_active_encounter": 1, "death_probability_per_infection": 1}
        summary = summarize_population(create_population(scenario), scenario)
        self.assertEqual(summary["states"]["D"], 0)
        self.assertEqual(summary["states"]["I"], scenario["initial_infectious"])

    def test_invalid_inputs(self):
        patches = [
            {"simulation_population": True}, {"simulation_population": 10001},
            {"age_lower_bounds_years": [0, 20, 20]}, {"age_lower_bounds_years": [1, 20]},
            {"age_group_counts": [1]}, {"age_group_counts": [40, 40, 40, 40, -1]},
            {"initial_infectious": 201}, {"random_seed": -1},
            {"death_probability_per_infection": float("nan")},
            {"transmission_probability_per_active_encounter": 1.1},
        ]
        for patch in patches:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                validate_scenario({**self.scenario, **patch})

    def test_empty_age_groups_remain_in_summary(self):
        scenario = {**self.scenario, "age_group_counts": [0, 0, 200, 0, 0]}
        summary = summarize_population(create_population(scenario), scenario)
        self.assertEqual([group["population"] for group in summary["age_groups"]], [0, 0, 200, 0, 0])


if __name__ == "__main__":
    unittest.main()
