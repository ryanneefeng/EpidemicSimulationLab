"""Check source data, population rounding, and contact aggregation."""

import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from src.country_data import aggregate_contacts, allocate_people, country_scenario, load_countries
from src.model import create_population, summarize_population


ROOT = Path(__file__).resolve().parents[1]


class CountryDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.countries = load_countries()
        cls.settings = json.loads((ROOT / "scenarios/example.json").read_text(encoding="utf-8"))

    def test_dataset_coverage_and_checksums(self):
        self.assertEqual(len(self.countries), 177)
        metadata = json.loads((ROOT / "data/SOURCES.json").read_text(encoding="utf-8"))
        for filename, checksum in metadata["outputs_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / "data" / filename).read_bytes()).hexdigest(), checksum)
        with (ROOT / "data/demographics.csv").open(encoding="utf-8", newline="") as handle:
            self.assertEqual(len(list(csv.DictReader(handle))), 201)

    def test_known_population_and_contact_values(self):
        country = self.countries["USA"]
        self.assertEqual(sum(country["population"]), 331002647)
        self.assertEqual(country["population"][0], 19676332)
        self.assertEqual(country["contacts"][0][0], 2.23647)
        self.assertEqual(country["contacts"][1][0], 1.32972)

    def test_weight_rows_and_sum_columns(self):
        self.assertEqual(aggregate_contacts([[1, 2], [3, 4]], [10, 30], [[0, 1]]), [[6]])
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        grouped = aggregate_contacts(matrix, [10, 30, 20], [[0, 1], [2]])
        self.assertEqual(grouped, [[7.5, 5.25], [15, 9]])

    def test_rounding_keeps_total_and_small_groups(self):
        self.assertEqual(allocate_people([1, 1, 1], 5), [2, 2, 1])
        self.assertEqual(allocate_people([1, 99], 1), [0, 1])
        with self.assertRaises(ValueError):
            allocate_people([0, 0], 10)

    def test_all_countries_and_group_widths(self):
        for country in self.countries.values():
            for width, oldest in ((5, 75), (10, 70), (20, 60)):
                with self.subTest(country=country["code"], width=width):
                    settings = {**self.settings, "age_group_width": width, "simulation_population": 20, "initial_infectious": 3}
                    scenario, population, matrix = country_scenario(country, settings)
                    self.assertEqual(sum(population), sum(country["population"]))
                    self.assertEqual(sum(scenario["age_group_counts"]), 20)
                    self.assertEqual(scenario["age_lower_bounds_years"][-1], oldest)
                    self.assertEqual(len(matrix), len(population))
                    self.assertTrue(all(len(row) == len(population) for row in matrix))
                    summary = summarize_population(create_population(scenario), scenario)
                    self.assertEqual(summary["states"], {"S": 17, "E": 0, "I": 3, "R": 0, "D": 0})

    def test_aggregation_preserves_total_contact_volume(self):
        country = self.countries["USA"]
        _, population, matrix = country_scenario(country, self.settings)
        original = sum(count * sum(row) for count, row in zip(country["population"], country["contacts"]))
        grouped = sum(count * sum(row) for count, row in zip(population, matrix))
        self.assertAlmostEqual(original / sum(population), grouped / sum(population), places=12)

    def test_terminal_interaction(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "model.py")],
            input="INVALID\nCAN\n20\n10\n3\n20\n50\n42\n", text=True,
            capture_output=True, cwd=ROOT, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Enter a country code or full name", result.stdout)
        self.assertIn("Canada (CAN)", result.stdout)
        self.assertIn("Transmission: 20%", result.stdout)
        self.assertIn("Mortality: 50%", result.stdout)
        self.assertIn("S=17, E=0, I=3, R=0, D=0", result.stdout)
        self.assertIn("Finished.", result.stdout)

    def test_example_finishes_without_input(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "model.py"), "--example"],
            text=True, capture_output=True, cwd=ROOT, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Country: United States of America (USA)", result.stdout)
        self.assertIn("S=199, E=0, I=1, R=0, D=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
