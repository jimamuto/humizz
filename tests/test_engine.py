import unittest

from humizz.adapters import FakeAdapter
from humizz.engine import RewriteEngine, RewriteRequest, build_prompt


class RewriteEngineTests(unittest.TestCase):
    def test_rewrites_with_fake_adapter(self):
        engine = RewriteEngine(FakeAdapter())
        result = engine.rewrite(RewriteRequest(text="This solution provides significant utility."))

        self.assertEqual(result.mode, "natural")
        self.assertIn("Humanized:", result.text)
        self.assertEqual(result.metadata["adapter"], "fake")

    def test_rejects_unknown_mode(self):
        engine = RewriteEngine(FakeAdapter())

        with self.assertRaisesRegex(ValueError, "Unknown mode"):
            engine.rewrite(RewriteRequest(text="Hello", mode="wrong"))

    def test_rejects_empty_input(self):
        engine = RewriteEngine(FakeAdapter())

        with self.assertRaisesRegex(ValueError, "Input text cannot be empty"):
            engine.rewrite(RewriteRequest(text=" "))

    def test_prompt_preserves_input(self):
        prompt = build_prompt("Rewrite naturally.", "Keep this meaning.")

        self.assertIn("Rewrite naturally.", prompt)
        self.assertIn("Original text:\nKeep this meaning.", prompt)


if __name__ == "__main__":
    unittest.main()
