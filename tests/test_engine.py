import unittest

from humizz.adapters import GenerationRequest, GenerationResult
from humizz.engine import RewriteEngine, RewriteRequest, build_prompt


class RetryAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, request: GenerationRequest) -> GenerationResult:
        self.calls += 1
        if self.calls == 1:
            return GenerationResult(
                text="Furthermore, this significant solution ensures substantial utility for users across many different practical contexts.",
                metadata={"adapter": "retry"},
            )
        return GenerationResult(text="This solution is useful.", metadata={"adapter": "retry"})


class StubAdapter:
    def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(text="This solution is useful.", metadata={"adapter": "stub"})


class RewriteEngineTests(unittest.TestCase):
    def test_rewrites_with_adapter(self):
        engine = RewriteEngine(StubAdapter())
        result = engine.rewrite(RewriteRequest(text="This solution provides significant utility."))

        self.assertEqual(result.mode, "natural")
        self.assertEqual(result.text, "This solution is useful.")
        self.assertEqual(result.metadata["adapter"], "stub")

    def test_rejects_unknown_mode(self):
        engine = RewriteEngine(StubAdapter())

        with self.assertRaisesRegex(ValueError, "Unknown mode"):
            engine.rewrite(RewriteRequest(text="Hello", mode="wrong"))

    def test_rejects_empty_input(self):
        engine = RewriteEngine(StubAdapter())

        with self.assertRaisesRegex(ValueError, "Input text cannot be empty"):
            engine.rewrite(RewriteRequest(text=" "))

    def test_prompt_preserves_input(self):
        prompt = build_prompt("Rewrite naturally.", "Keep this meaning.")

        self.assertIn("Rewrite naturally.", prompt)
        self.assertIn("<original>\nKeep this meaning.\n</original>", prompt)

    def test_retries_and_keeps_better_output(self):
        adapter = RetryAdapter()
        engine = RewriteEngine(adapter)

        result = engine.rewrite(RewriteRequest(text="This solution provides significant utility."))

        self.assertEqual(adapter.calls, 2)
        self.assertEqual(result.text, "This solution is useful.")
        self.assertEqual(result.metadata["attempt"], 2)

    def test_retry_prompt_includes_warning_guidance(self):
        prompt = build_prompt("Rewrite naturally.", "Keep this meaning.", retry_warnings=("too-formal",))

        self.assertIn("Use plainer, everyday words.", prompt)


if __name__ == "__main__":
    unittest.main()
