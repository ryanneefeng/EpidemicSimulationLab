"""Check disease timing, spread probabilities, and population accounting."""

import math
import random
import unittest

from src.model import DiseaseState as State, Person, validate_scenario
from src.simulation import advance_disease, infection_probabilities, simulate, validate_contacts


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


class SimulationTests(unittest.TestCase):
    def test_synchronous_timing_with_certain_exposure(self):
        result = simulate(toy_scenario(latent_days=1, infectious_days=1), [[10000]])
        self.assertEqual([(r["S"], r["E"], r["I"], r["R"]) for r in result["history"]],
                         [(2, 0, 1, 0), (0, 2, 0, 1), (0, 0, 2, 1), (0, 0, 0, 3)])

    def test_accounting_flows_and_absorbing_states(self):
        result = simulate(toy_scenario(simulation_population=60, age_group_counts=[60],
                                       death_probability_per_infection=0.5), [[4]])
        for previous, row in zip(result["history"], result["history"][1:]):
            self.assertEqual(sum(row[s] for s in "SEIRD"), 60)
            self.assertTrue(all(row[s] >= 0 for s in "SEIRD"))
            self.assertEqual(row["S"], previous["S"] - row["new_exposures"])
            self.assertEqual(row["E"], previous["E"] + row["new_exposures"] - row["new_infectious"])
            self.assertEqual(row["I"], previous["I"] + row["new_infectious"] - row["new_recoveries"] - row["new_deaths"])
            self.assertEqual(row["R"], previous["R"] + row["new_recoveries"])
            self.assertEqual(row["D"], previous["D"] + row["new_deaths"])

    def test_no_spread_limits(self):
        for changes, matrix in (({"initial_infectious": 0}, [[5]]),
                                ({"transmission_probability_per_active_encounter": 0}, [[5]]),
                                ({}, [[0]])):
            scenario = toy_scenario(**changes)
            result = simulate(scenario, matrix)
            self.assertEqual(result["metrics"]["total_infections"], scenario["initial_infectious"])
            self.assertEqual(result["metrics"]["unresolved"], 0)

    def test_repeatability_and_independent_random_streams(self):
        scenario = toy_scenario(simulation_population=60, age_group_counts=[60], simulation_days=100)
        state = random.getstate()
        recovered = simulate(scenario, [[4]])
        self.assertEqual(recovered, simulate(scenario, [[4]]))
        fatal = simulate({**scenario, "death_probability_per_infection": 1}, [[4]])
        self.assertEqual(random.getstate(), state)
        self.assertEqual([(r["S"], r["E"], r["I"]) for r in recovered["history"]],
                         [(r["S"], r["E"], r["I"]) for r in fatal["history"]])
        self.assertEqual(fatal["metrics"]["deaths"], fatal["metrics"]["total_infections"])
        self.assertEqual(recovered["metrics"]["deaths"], 0)

    def test_horizon_censoring_and_single_person(self):
        result = simulate(toy_scenario(simulation_days=1), [[0]])
        self.assertEqual(result["metrics"]["unresolved"], 1)
        self.assertIsNone(result["metrics"]["extinction_day"])
        result = simulate(toy_scenario(simulation_population=1, age_group_counts=[1]), [[5]])
        self.assertEqual(result["metrics"]["total_infections"], 1)

    def test_one_day_infections_match_binomial_expectation(self):
        scenario = toy_scenario(simulation_population=10000, age_group_counts=[10000],
                                initial_infectious=1000, simulation_days=1)
        result = simulate(scenario, [[5]])
        risk = 1 - math.exp(-0.2 * 5 * 1000 / 9999)
        mean = 9000 * risk
        sd = math.sqrt(9000 * risk * (1 - risk))
        self.assertLess(abs(result["history"][1]["new_exposures"] - mean), 6 * sd)


if __name__ == "__main__":
    unittest.main()
