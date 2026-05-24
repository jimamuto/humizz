import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from humizz.adapters import GenerationRequest, GenerationResult
from humizz.eval import main


class StubAdapter:
    def generate(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(text="This is a useful test.", metadata={"adapter": "stub"})


class EvalTests(unittest.TestCase):
    def test_eval_writes_all_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "input.txt"
            output_path = Path(tmp) / "out.json"
            input_path.write_text("This is a useful test.", encoding="utf-8")

            with patch("humizz.eval.make_adapter", return_value=StubAdapter()):
                code = main([str(input_path), "--output", str(output_path)])

            self.assertEqual(code, 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["results"]), 4)


if __name__ == "__main__":
    unittest.main()
