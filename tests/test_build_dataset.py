import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_dataset import build_dataset, feedback_to_examples, normalize_text


class BuildDatasetTests(unittest.TestCase):
    def test_normalizes_text(self):
        self.assertEqual(normalize_text("  This\n is\t useful. "), "This is useful.")

    def test_feedback_to_examples_prefers_human_rewrite(self):
        rows = [
            {
                "input": "It is important to note that this solution provides significant utility.",
                "output": "This solution provides useful value.",
                "accepted": False,
                "preferred_rewrite": "This solution is useful.",
            },
            {
                "input": "Rejected without a replacement.",
                "output": "Rejected output.",
                "accepted": False,
            },
        ]

        examples = feedback_to_examples(rows)

        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]["input"], rows[0]["input"])
        self.assertEqual(examples[0]["output"], "This solution is useful.")

    def test_build_dataset_writes_splits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "feedback.jsonl"
            output_dir = root / "dataset"
            rows = [
                {"input": f"Input {idx}", "output": f"Output {idx}", "accepted": True}
                for idx in range(10)
            ]
            input_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

            counts = build_dataset(input_path, output_dir, seed=1)

            total = sum(counts.values())
            train_rows = output_dir.joinpath("train.jsonl").read_text(encoding="utf-8").splitlines()
            validation_rows = output_dir.joinpath("validation.jsonl").read_text(encoding="utf-8").splitlines()
            test_rows = output_dir.joinpath("test.jsonl").read_text(encoding="utf-8").splitlines()

        self.assertEqual(total, 10)
        self.assertEqual(len(train_rows), 8)
        self.assertEqual(len(validation_rows), 1)
        self.assertEqual(len(test_rows), 1)


if __name__ == "__main__":
    unittest.main()
