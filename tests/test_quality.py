import unittest

from humizz.quality import assess_quality, sentence_word_counts


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

    def test_formal_terms_warn(self):
        report = assess_quality("Use it.", "Furthermore, this significant method ensures substantial value.")

        self.assertIn("too-formal", report.warnings)
        self.assertGreater(report.formal_term_count, 0)

    def test_long_sentences_warn(self):
        output = "This sentence has many words because it keeps adding clauses and details without giving the reader a break or sounding like normal quick writing for people who want a clear and simple message."
        report = assess_quality("Short source text for testing.", output)

        self.assertIn("long-sentences", report.warnings)

    def test_sentence_word_counts(self):
        self.assertEqual(sentence_word_counts("Short one. This is longer."), [2, 3])


if __name__ == "__main__":
    unittest.main()
