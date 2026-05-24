import unittest

from scripts.extract_public_datasets import pair_direct_rows, pair_parallel_rows


class ExtractPublicDatasetsTests(unittest.TestCase):
    def test_pair_direct_rows(self):
        rows = [
            {"ai_text": "AI generated text.", "human_text": "Human text."},
            {"ai_text": "AI generated text.", "human_text": "Human text."},
            {"ai_text": "", "human_text": "Skipped."},
        ]

        pairs = pair_direct_rows(rows, "ai_text", "human_text")

        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["input"], "AI generated text.")
        self.assertEqual(pairs[0]["output"], "Human text.")

    def test_pair_parallel_rows(self):
        rows = [
            {"doc_id": "doc1", "source": "chunk_1", "text": "Human version."},
            {"doc_id": "doc1", "source": "gpt-4", "text": "AI version."},
            {"doc_id": "doc2", "source": "gpt-4", "text": "No human match."},
        ]

        pairs = pair_parallel_rows(
            rows,
            group_field="doc_id",
            source_field="source",
            text_field="text",
            human_source_contains="chunk",
        )

        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["input"], "AI version.")
        self.assertEqual(pairs[0]["output"], "Human version.")


if __name__ == "__main__":
    unittest.main()
