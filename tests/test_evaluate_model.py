import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from humizz.adapters import GenerationRequest, GenerationResult
from scripts.evaluate_model import evaluate_dataset


class StubAdapter:
    def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(text="This solution is useful.", metadata={"adapter": "stub"})


class EvaluateModelTests(unittest.TestCase):
    def test_evaluates_jsonl_dataset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "test.jsonl"
            dataset_path.write_text(
                json.dumps({"input": "This solution provides significant utility.", "output": "This solution is useful."}) + "\n",
                encoding="utf-8",
            )

            with patch("scripts.evaluate_model.make_adapter", return_value=StubAdapter()):
                payload = evaluate_dataset(dataset_path, backend="modal", model="stub")

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["exact_match_rate"], 1.0)
        self.assertEqual(payload["examples"][0]["actual"], "This solution is useful.")


if __name__ == "__main__":
    unittest.main()
