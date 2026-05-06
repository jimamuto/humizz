import unittest

from humizz.quality import assess_quality


class QualityTests(unittest.TestCase):
    def test_valid_output_has_no_warnings(self):
        report = assess_quality("This is a useful draft.", "This draft is useful.")

        self.assertEqual(report.warnings, ())

    def test_empty_output_warns(self):
        report = assess_quality("Some input", "")

        self.assertIn("empty-output", report.warnings)

    def test_large_shrink_warns(self):
        report = assess_quality("This is a long enough sentence for shrink testing.", "Short.")

        self.assertIn("large-shrink", report.warnings)

    def test_large_expansion_warns(self):
        report = assess_quality("Short.", "This is much longer than the source text and should trigger expansion.")

        self.assertIn("large-expansion", report.warnings)


if __name__ == "__main__":
    unittest.main()
