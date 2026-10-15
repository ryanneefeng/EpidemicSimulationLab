"""Check disease timing, spread probabilities, and population accounting."""

import random
import unittest

from src.model import DiseaseState as State, Person, validate_scenario
from src.simulation import advance_disease


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


if __name__ == "__main__":
    unittest.main()
