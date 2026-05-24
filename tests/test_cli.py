import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from humizz.adapters import GenerationRequest, GenerationResult
from humizz.cli import main


class StubAdapter:
    def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(text="This is useful.", metadata={"adapter": "stub"})


class CliTests(unittest.TestCase):
    def test_cli_prints_plain_text(self):
        stdout = io.StringIO()

        with patch("humizz.cli.make_adapter", return_value=StubAdapter()):
            with redirect_stdout(stdout):
                code = main(["This is useful.", "--mode", "natural"])

        self.assertEqual(code, 0)
        self.assertIn("This is useful.", stdout.getvalue())

    def test_cli_prints_json(self):
        stdout = io.StringIO()

        with patch("humizz.cli.make_adapter", return_value=StubAdapter()):
            with redirect_stdout(stdout):
                code = main(["This is useful.", "--json"])

        self.assertEqual(code, 0)
        self.assertIn('"quality"', stdout.getvalue())

    def test_cli_logs_feedback(self):
        stdout = io.StringIO()

        with tempfile.TemporaryDirectory() as tmpdir:
            feedback_path = Path(tmpdir) / "feedback.jsonl"
            with patch("humizz.cli.make_adapter", return_value=StubAdapter()):
                with redirect_stdout(stdout):
                    code = main(
                        [
                            "This is useful.",
                            "--log-feedback",
                            "--feedback-path",
                            str(feedback_path),
                            "--accepted",
                            "no",
                            "--detector-score",
                            "0.98",
                            "--preferred-rewrite",
                            "This helps.",
                        ]
                    )

            rows = feedback_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(code, 0)
        self.assertEqual(len(rows), 1)
        payload = json.loads(rows[0])
        self.assertEqual(payload["input"], "This is useful.")
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["detector_score"], 0.98)
        self.assertEqual(payload["preferred_rewrite"], "This helps.")


if __name__ == "__main__":
    unittest.main()
