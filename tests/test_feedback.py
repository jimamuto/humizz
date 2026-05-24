import json
import tempfile
import unittest
from pathlib import Path

from humizz.engine import RewriteRequest, RewriteResult
from humizz.feedback import append_feedback, build_feedback_record
from humizz.quality import assess_quality


class FeedbackTests(unittest.TestCase):
    def test_builds_feedback_record(self):
        request = RewriteRequest(text="This solution provides significant utility.", mode="natural", max_attempts=2)
        result = RewriteResult(
            text="This solution is useful.",
            mode="natural",
            quality=assess_quality(request.text, "This solution is useful."),
            metadata={"adapter": "stub"},
        )

        record = build_feedback_record(
            request,
            result,
            accepted=False,
            detector_score=0.98,
            preferred_rewrite="This helps.",
        )

        self.assertEqual(record.input, request.text)
        self.assertEqual(record.output, result.text)
        self.assertFalse(record.accepted)
        self.assertEqual(record.detector_score, 0.98)
        self.assertEqual(record.preferred_rewrite, "This helps.")
        self.assertEqual(record.metadata["adapter"], "stub")
        self.assertEqual(record.metadata["max_attempts"], 2)

    def test_appends_feedback_jsonl(self):
        request = RewriteRequest(text="This solution provides significant utility.")
        result = RewriteResult(
            text="This solution is useful.",
            mode="natural",
            quality=assess_quality(request.text, "This solution is useful."),
            metadata={"adapter": "stub"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "feedback.jsonl"
            append_feedback(build_feedback_record(request, result, accepted=True), path)

            rows = path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(len(rows), 1)
        payload = json.loads(rows[0])
        self.assertEqual(payload["input"], request.text)
        self.assertEqual(payload["output"], result.text)
        self.assertTrue(payload["accepted"])


if __name__ == "__main__":
    unittest.main()
