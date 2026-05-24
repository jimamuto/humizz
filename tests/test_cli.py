import io
import unittest
from contextlib import redirect_stdout
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


if __name__ == "__main__":
    unittest.main()
