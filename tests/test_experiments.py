"""Check repeated-run summaries and saved provenance."""

import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.experiments import run_study, save_study, summarize_runs
from test_simulation import toy_scenario


class ExperimentTests(unittest.TestCase):
    def test_known_sample_statistics_and_censoring(self):
        rows = [
            {"attack_fraction": 0.25, "deaths": 0, "secondary_infections": 0, "unresolved": 0},
            {"attack_fraction": 0.75, "deaths": 2, "secondary_infections": 2, "unresolved": 1},
        ]
        summary = summarize_runs(rows)
        self.assertEqual(summary["attack_percent_mean"], 50)
        self.assertAlmostEqual(summary["attack_percent_sd"], 50 / 2 ** 0.5)
        self.assertAlmostEqual(summary["attack_percent_mcse"], 25)
        self.assertEqual(summary["deaths_mean"], 1)
        self.assertAlmostEqual(summary["deaths_mcse"], 1)
        self.assertEqual(summary["no_secondary_fraction"], 0.5)
        self.assertEqual(summary["unresolved_runs"], 1)

    def test_complete_design_and_saved_inputs(self):
        result = run_study(toy_scenario(), [[0]], replicates=2)
        self.assertEqual(len(result["rows"]), 8)
        self.assertEqual(len(result["summary"]), 4)
        self.assertTrue(all(row["secondary_infections"] == 0 for row in result["rows"]))
        workspace = Path(__file__).resolve().parents[1]
        results = workspace / "results"
        results.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=results) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(workspace))
            save_study(result, directory)
            report = json.loads((Path(directory) / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(report["contact_matrix"], [[0]])
            self.assertEqual(report["seed_range_inclusive"], [0, 1])
            path = Path(directory) / "replicates.csv"
            self.assertEqual(report["replicates_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            with path.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(len(list(csv.DictReader(handle))), 8)


if __name__ == "__main__":
    unittest.main()
