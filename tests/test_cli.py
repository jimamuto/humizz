import io
import unittest
from contextlib import redirect_stdout

from humizz.cli import main


class CliTests(unittest.TestCase):
    def test_cli_prints_plain_text(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(["This is useful.", "--mode", "natural"])

        self.assertEqual(code, 0)
        self.assertIn("Humanized:", stdout.getvalue())

    def test_cli_prints_json(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            code = main(["This is useful.", "--json"])

        self.assertEqual(code, 0)
        self.assertIn('"quality"', stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
