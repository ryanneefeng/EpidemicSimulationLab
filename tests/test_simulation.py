"""Check disease timing, spread probabilities, and population accounting."""

import math
import random
import unittest

from src.model import DiseaseState as State, Person, validate_scenario
from src.simulation import advance_disease, infection_probabilities, validate_contacts


def toy_scenario(**changes):
    return {
        "name": "Hand calculation", "simulation_population": 3,
        "age_lower_bounds_years": [0], "age_group_counts": [3],
        "initial_infectious": 1, "random_seed": 42,
        "transmission_probability_per_active_encounter": 0.2,
        "death_probability_per_infection": 0.0,
        "latent_days": 2, "infectious_days": 3, "simulation_days": 10,
        **changes,
    }


class DiseaseTimingTests(unittest.TestCase):
    def test_hand_trace_and_no_instant_chain(self):
        people = [Person(1, "0+", State.INFECTIOUS), Person(2, "0+"), Person(3, "0+")]
        rng = random.Random(1)
        expected = ["IES", "IES", "RIS", "RIS", "RIS", "RRS"]
        for day, states in enumerate(expected, start=1):
            advance_disease(people, toy_scenario(), {2} if day == 1 else set(), rng)
            self.assertEqual("".join(p.state.value for p in people), states)

    def test_mortality_is_sampled_once_at_resolution(self):
        class CountingRandom:
            calls = 0

            def random(self):
                self.calls += 1
                return 0.5

        for fatality, end in ((0, State.RECOVERED), (1, State.DEAD)):
            rng = CountingRandom()
            people = [Person(1, "0+", State.INFECTIOUS)]
            for day in range(1, 9):
                advance_disease(people, toy_scenario(death_probability_per_infection=fatality), set(), rng)
                self.assertEqual(people[0].state, State.INFECTIOUS if day < 3 else end)
            self.assertEqual(rng.calls, 1)

    def test_invalid_exposure_does_not_mutate_population(self):
        people = [Person(1, "0+", State.INFECTIOUS)]
        with self.assertRaises(ValueError):
            advance_disease(people, toy_scenario(), {1}, random.Random(1))
        self.assertEqual(people[0].days_in_state, 0)

    def test_duration_validation(self):
        for key in ("latent_days", "infectious_days", "simulation_days"):
            for value in (0, -1, 1.5, True, 3651, None):
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    validate_scenario(toy_scenario(**{key: value}))


class TransmissionTests(unittest.TestCase):
    def test_row_orientation_and_self_exclusion(self):
        risks = infection_probabilities([[2, 3], [4, 5]], [5, 10], [4, 8], [1, 2], 0.2)
        self.assertAlmostEqual(risks[0], 1 - math.exp(-0.2 * (2 / 4 + 3 * 2 / 10)))
        self.assertAlmostEqual(risks[1], 1 - math.exp(-0.2 * (4 / 5 + 5 * 2 / 9)))

    def test_poisson_derivation_matches_explicit_sum(self):
        mean, probability = 2.5, 0.2
        no_infection = sum(math.exp(-mean) * mean ** k / math.factorial(k)
                           * (1 - probability) ** k for k in range(50))
        risk = infection_probabilities([[mean]], [2], [1], [1], probability)[0]
        self.assertAlmostEqual(risk, 1 - no_infection, places=14)

    def test_zero_sources_and_empty_groups(self):
        self.assertEqual(infection_probabilities([[5]], [1], [1], [0], 1), [0])
        self.assertEqual(infection_probabilities([[5]], [2], [1], [1], 0), [0])
        self.assertEqual(infection_probabilities([[0]], [2], [1], [1], 1), [0])
        self.assertEqual(infection_probabilities([[5, 5], [5, 5]], [2, 0], [0, 0], [2, 0], 1), [0, 0])

    def test_certain_transmission_still_requires_an_encounter(self):
        risk = infection_probabilities([[1]], [2], [1], [1], 1)[0]
        self.assertAlmostEqual(risk, 1 - math.exp(-1))
        self.assertLess(risk, 1)

    def test_invalid_matrix(self):
        for matrix in ([[1, 2]], [[-1]], [[float("nan")]], [[float("inf")]], [[True]]):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                validate_contacts(matrix, 1)


if __name__ == "__main__":
    unittest.main()
